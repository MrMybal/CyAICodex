import hashlib
import json
import re
import secrets
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field, model_validator
from typing import Literal


def now():
    return datetime.now(timezone.utc).isoformat()


class Method(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    summary: str = Field(default="", max_length=600)
    content: str = Field(min_length=1, max_length=100000)
    category: str = Field(default="Général", min_length=1, max_length=80)
    tags: list[str] = Field(default_factory=list, max_length=30)
    scope: Literal["global", "type", "project"] = "global"
    scope_id: str = ""
    status: Literal["published", "draft", "archived"] = "published"

    @model_validator(mode="after")
    def clean(self):
        self.title = self.title.strip()
        if not self.title or not self.content.strip():
            raise ValueError("Le titre et le contenu sont obligatoires.")
        self.tags = list(dict.fromkeys(t.strip() for t in self.tags if t.strip()))
        if any(len(t) > 60 for t in self.tags):
            raise ValueError("Un tag ne peut pas dépasser 60 caractères.")
        if self.scope == "global":
            self.scope_id = ""
        elif not self.scope_id:
            raise ValueError("Choisissez un projet ou un type de projet.")
        return self


class Conflict(ValueError):
    pass


class Store:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.path = self.folder / "methodes.sqlite3"
        with self.db() as db:
            db.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS types(id TEXT PRIMARY KEY, name TEXT UNIQUE NOT NULL);
            CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY, name TEXT UNIQUE NOT NULL,
              type_id TEXT REFERENCES types(id));
            CREATE TABLE IF NOT EXISTS methods(id TEXT PRIMARY KEY, title TEXT, summary TEXT,
              content TEXT, category TEXT, tags TEXT, scope TEXT, scope_id TEXT, status TEXT,
              version INTEGER, created_at TEXT, updated_at TEXT);
            CREATE TABLE IF NOT EXISTS history(method_id TEXT, version INTEGER, snapshot TEXT,
              author TEXT, at TEXT, PRIMARY KEY(method_id,version));
            CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(
              id UNINDEXED, title, summary, tags, content, tokenize='unicode61 remove_diacritics 2');
            CREATE TABLE IF NOT EXISTS connections(id TEXT PRIMARY KEY, name TEXT, token_hash TEXT UNIQUE,
              project_id TEXT, type_id TEXT, include_global INTEGER, writable INTEGER, last_seen TEXT);
            CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
            """)
            if not db.execute("SELECT 1 FROM settings WHERE key='admin_token'").fetchone():
                db.execute("INSERT INTO settings VALUES('admin_token',?)", (secrets.token_urlsafe(32),))

    @contextmanager
    def db(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def setting(self, key, default=""):
        with self.db() as db:
            row = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            return row[0] if row else default

    def set_setting(self, key, value):
        with self.db() as db:
            db.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", (key, value))

    def catalog(self):
        with self.db() as db:
            return {table: [dict(r) for r in db.execute(f"SELECT * FROM {table} ORDER BY name")]
                    for table in ("types", "projects")}

    def add_group(self, kind, name, type_id=None):
        name = name.strip()
        if kind not in ("types", "projects") or not name or len(name) > 100:
            raise ValueError("Nom de groupe invalide.")
        item = {"id": uuid.uuid4().hex, "name": name}
        with self.db() as db:
            if kind == "types":
                db.execute("INSERT INTO types VALUES(:id,:name)", item)
            else:
                item["type_id"] = type_id or None
                db.execute("INSERT INTO projects VALUES(:id,:name,:type_id)", item)
        return item

    @staticmethod
    def decode(row):
        if row is None:
            raise KeyError("Méthode introuvable.")
        d = dict(row)
        d["tags"] = json.loads(d["tags"])
        return d

    def context(self, project_id="", type_id="", include_global=True):
        with self.db() as db:
            if project_id:
                row = db.execute("SELECT type_id FROM projects WHERE id=?", (project_id,)).fetchone()
                if not row:
                    raise ValueError("Projet inconnu.")
                type_id = row[0] or ""
            elif type_id and not db.execute("SELECT 1 FROM types WHERE id=?", (type_id,)).fetchone():
                raise ValueError("Type de projet inconnu.")
        return {"project_id": project_id, "type_id": type_id, "include_global": include_global}

    @staticmethod
    def allowed(method, context):
        if context is None:
            return True
        return ((method["scope"] == "global" and context["include_global"])
                or (method["scope"] == "project" and bool(context["project_id"])
                    and method["scope_id"] == context["project_id"])
                or (method["scope"] == "type" and bool(context["type_id"])
                    and method["scope_id"] == context["type_id"]))

    def get(self, method_id, context=None):
        with self.db() as db:
            result = self.decode(db.execute("SELECT * FROM methods WHERE id=?", (method_id,)).fetchone())
        if not self.allowed(result, context) or (context is not None and result["status"] != "published"):
            raise KeyError("Méthode introuvable dans ce contexte.")
        return result

    def save(self, method: Method, method_id=None, version=None, author="Vous", context=None):
        data = method.model_dump()
        if not self.allowed(data, context):
            raise ValueError("Cette méthode ne correspond pas au contexte de la connexion.")
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            if method.scope != "global":
                table = "types" if method.scope == "type" else "projects"
                if not db.execute(f"SELECT 1 FROM {table} WHERE id=?", (method.scope_id,)).fetchone():
                    raise ValueError("Le groupe choisi n'existe pas.")
            existing = None
            if method_id:
                existing = self.decode(db.execute("SELECT * FROM methods WHERE id=?", (method_id,)).fetchone())
                if not self.allowed(existing, context):
                    raise KeyError("Méthode introuvable dans ce contexte.")
                if version != existing["version"]:
                    raise Conflict("La méthode a changé. Rechargez-la avant d'enregistrer.")
            data.update(id=method_id or uuid.uuid4().hex,
                        version=existing["version"] + 1 if existing else 1,
                        created_at=existing["created_at"] if existing else now(), updated_at=now())
            db.execute("INSERT INTO history VALUES(?,?,?,?,?)",
                       (data["id"], data["version"], json.dumps(data, ensure_ascii=False), author, now()))
            sql_data = {**data, "tags": json.dumps(data["tags"], ensure_ascii=False)}
            columns = ",".join(sql_data)
            db.execute(f"INSERT OR REPLACE INTO methods({columns}) VALUES({','.join(':'+k for k in sql_data)})", sql_data)
            db.execute("DELETE FROM search WHERE id=?", (data["id"],))
            db.execute("INSERT INTO search VALUES(?,?,?,?,?)", (data["id"], data["title"],
                       data["summary"], " ".join(data["tags"]), data["content"]))
            return data

    def search(self, query="", context=None, category="", status="published", limit=50, offset=0):
        clauses, args = [], []
        query_tokens = re.findall(r"\w+", query, re.UNICODE)[:20]
        join, order = "", "m.updated_at DESC"
        if query_tokens:
            join = " JOIN search s ON s.id=m.id"
            clauses.append("search MATCH ?")
            args.append(" AND ".join('"'+t+'"*' for t in query_tokens))
            order = "bm25(search,0,8,4,5,1),m.updated_at DESC"
        if context is not None:
            scope_clauses = []
            if context["include_global"]:
                scope_clauses.append("m.scope='global'")
            for scope, key in (("project", "project_id"), ("type", "type_id")):
                if context[key]:
                    scope_clauses.append("(m.scope=? AND m.scope_id=?)")
                    args.extend([scope, context[key]])
            clauses.append("(" + " OR ".join(scope_clauses or ["0"]) + ")")
        if status:
            clauses.append("m.status=?")
            args.append(status)
        if category:
            clauses.append("m.category=?")
            args.append(category)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with self.db() as db:
            total = db.execute("SELECT count(*) FROM methods m"+join+where, args).fetchone()[0]
            rows = db.execute("SELECT m.* FROM methods m"+join+where+" ORDER BY "+order+" LIMIT ? OFFSET ?",
                              [*args, max(1, min(limit, 100)), max(0, offset)]).fetchall()
        items = []
        for row in rows:
            d = self.decode(row)
            d["excerpt"] = d.pop("content")[:240]
            items.append(d)
        return {"items": items, "total": total}

    def history(self, method_id):
        with self.db() as db:
            return [{**dict(r), "snapshot": json.loads(r["snapshot"])} for r in db.execute(
                "SELECT * FROM history WHERE method_id=? ORDER BY version DESC", (method_id,))]

    def new_connection(self, name, project_id="", type_id="", include_global=True, writable=False):
        context = self.context(project_id, type_id, include_global)
        token = secrets.token_urlsafe(32)
        data = dict(id=uuid.uuid4().hex, name=name, token_hash=hashlib.sha256(token.encode()).hexdigest(),
                    **context, writable=writable, last_seen=None)
        with self.db() as db:
            db.execute("INSERT INTO connections VALUES(:id,:name,:token_hash,:project_id,:type_id,:include_global,:writable,:last_seen)", data)
        return {"id": data["id"], "token": token}

    def authenticate(self, token):
        with self.db() as db:
            row = db.execute("SELECT * FROM connections WHERE token_hash=?", (hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
            if not row:
                return None
            db.execute("UPDATE connections SET last_seen=? WHERE id=?", (now(), row["id"]))
            return dict(row)

    def connections(self):
        with self.db() as db:
            return [dict(r) for r in db.execute("SELECT id,name,project_id,type_id,include_global,writable,last_seen FROM connections")]

    def revoke(self, connection_id):
        with self.db() as db:
            db.execute("DELETE FROM connections WHERE id=?", (connection_id,))

    def export(self):
        with self.db() as db:
            return {"format": "methodes-v1", **self.catalog(), "methods": [self.decode(r) for r in db.execute("SELECT * FROM methods")]}

    def metadata(self):
        with self.db() as db:
            return {"categories": [r[0] for r in db.execute("SELECT DISTINCT category FROM methods ORDER BY category")],
                    "published": db.execute("SELECT count(*) FROM methods WHERE status='published'").fetchone()[0]}
