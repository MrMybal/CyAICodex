"""Original image files with searchable, versioned usage instructions."""
import base64
import hashlib
import json
import re
import uuid
import warnings
from io import BytesIO
from pathlib import Path
from typing import Literal

from PIL import Image, ImageOps, UnidentifiedImageError
from pydantic import BaseModel, Field, model_validator

from .store import Conflict, now

MAX_BYTES = 20 * 1024 * 1024


class ImageDescription(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=30000)
    preserve: str = Field(default="", max_length=15000)
    avoid: str = Field(default="", max_length=15000)
    usage: str = Field(default="", max_length=15000)
    source: str = Field(default="", max_length=2000)
    category: str = Field(default="Référence", min_length=1, max_length=80)
    tags: list[str] = Field(default_factory=list, max_length=30)
    scope: Literal["global", "type", "project"] = "global"
    scope_id: str = ""
    status: Literal["published", "draft", "archived"] = "published"

    @model_validator(mode="after")
    def clean(self):
        self.title = self.title.strip()
        if not self.title or not self.description.strip():
            raise ValueError("Le titre et la description sont obligatoires.")
        self.tags = list(dict.fromkeys(t.strip() for t in self.tags if t.strip()))
        if any(len(t) > 60 for t in self.tags):
            raise ValueError("Un tag ne peut pas dépasser 60 caractères.")
        if self.scope == "global":
            self.scope_id = ""
        elif not self.scope_id:
            raise ValueError("Choisissez un projet ou un type de projet.")
        return self


class ImageLibrary:
    def __init__(self, store):
        self.store = store
        self.folder = store.folder / "images"
        self.folder.mkdir(exist_ok=True)
        with store.db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS images(id TEXT PRIMARY KEY, metadata TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS image_history(id TEXT, version INTEGER, snapshot TEXT,
                author TEXT, at TEXT, PRIMARY KEY(id,version));
            CREATE VIRTUAL TABLE IF NOT EXISTS image_search USING fts5(id UNINDEXED,
                title, tags, description, instructions, tokenize='unicode61 remove_diacritics 2');
            """)

    def validate_scope(self, description, db):
        if description.scope != "global":
            table = "types" if description.scope == "type" else "projects"
            if not db.execute(f"SELECT 1 FROM {table} WHERE id=?", (description.scope_id,)).fetchone():
                raise ValueError("Le groupe choisi n'existe pas.")

    @staticmethod
    def inspect(raw):
        if not raw or len(raw) > MAX_BYTES:
            raise ValueError("Choisissez une image de 20 Mo maximum.")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(raw)) as image:
                    if image.format not in ("PNG", "JPEG", "WEBP"):
                        raise ValueError("Formats acceptés : PNG, JPEG et WebP.")
                    if max(image.size) > 8192 or image.width * image.height > 25_000_000:
                        raise ValueError("Image trop grande : maximum 8192 pixels par côté et 25 mégapixels.")
                    if getattr(image, "is_animated", False):
                        raise ValueError("Utilisez une image fixe, sans animation.")
                    info = {"width": image.width, "height": image.height,
                            "mime": Image.MIME[image.format],
                            "extension": {"PNG":"png", "JPEG":"jpg", "WEBP":"webp"}[image.format]}
                    image.verify()
                with Image.open(BytesIO(raw)) as image:
                    image.load()
                    info["transparent"] = image.convert("RGBA").getextrema()[3][0] < 255
            return info
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
            raise ValueError("Le fichier n'est pas une image valide ou dépasse les limites autorisées.") from exc

    def _write(self, db, data, author):
        encoded = json.dumps(data, ensure_ascii=False)
        db.execute("INSERT OR REPLACE INTO images VALUES(?,?)", (data["id"], encoded))
        db.execute("INSERT INTO image_history VALUES(?,?,?,?,?)", (data["id"],data["version"],encoded,author,now()))
        db.execute("DELETE FROM image_search WHERE id=?", (data["id"],))
        db.execute("INSERT INTO image_search VALUES(?,?,?,?,?)", (data["id"],data["title"]," ".join(data["tags"]),
            data["description"],"\n".join(data[k] for k in ("preserve","avoid","usage","category","source"))))

    def add(self, raw, description: ImageDescription, author="Vous", context=None):
        if not self.store.allowed(description.model_dump(), context):
            raise ValueError("Cette portée n'est pas accessible à la connexion.")
        info = self.inspect(raw)
        identifier = uuid.uuid4().hex
        data = {**description.model_dump(), **info, "id":identifier, "version":1,
                "bytes":len(raw), "sha256":hashlib.sha256(raw).hexdigest(), "created_at":now(), "updated_at":now()}
        path = self.folder / (identifier+"."+info["extension"])
        try:
            with self.store.db() as db:
                db.execute("BEGIN IMMEDIATE")
                self.validate_scope(description, db)
                path.write_bytes(raw)
                self._write(db, data, author)
        except Exception:
            path.unlink(missing_ok=True)
            raise
        return data

    def get(self, identifier, context=None):
        with self.store.db() as db:
            row = db.execute("SELECT metadata FROM images WHERE id=?", (identifier,)).fetchone()
        if not row:
            raise KeyError("Image introuvable.")
        data = json.loads(row[0])
        if not self.store.allowed(data, context) or (context is not None and data["status"] != "published"):
            raise KeyError("Image introuvable dans ce contexte.")
        return data

    def path(self, identifier, context=None):
        data = self.get(identifier, context)
        return self.folder / (data["id"]+"."+data["extension"])

    def update(self, identifier, description, version, author="Vous", context=None):
        with self.store.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT metadata FROM images WHERE id=?", (identifier,)).fetchone()
            if not row:
                raise KeyError("Image introuvable.")
            current = json.loads(row[0])
            if not self.store.allowed(current, context) or (context is not None and current["status"] != "published"):
                raise KeyError("Image introuvable dans ce contexte.")
            if not self.store.allowed(description.model_dump(), context):
                raise ValueError("Cette portée n'est pas accessible à la connexion.")
            if current["version"] != version:
                raise Conflict("Cette ressource a changé. Rechargez-la avant d'enregistrer.")
            self.validate_scope(description, db)
            data = {**current, **description.model_dump(), "version":version+1,"updated_at":now()}
            self._write(db, data, author)
        return data

    def search(self, query="", context=None, status="published", limit=24, offset=0):
        clauses, args = [], []
        tokens = re.findall(r"\w+", query, re.UNICODE)[:20]
        join, order = "", "json_extract(i.metadata,'$.updated_at') DESC"
        if tokens:
            join = " JOIN image_search s ON s.id=i.id"
            clauses.append("image_search MATCH ?")
            args.append(" AND ".join('"'+t+'"*' for t in tokens))
            order = "bm25(image_search,0,8,5,3,2)"
        if status:
            clauses.append("json_extract(i.metadata,'$.status')=?")
            args.append(status)
        if context is not None:
            scopes = []
            if context["include_global"]:
                scopes.append("json_extract(i.metadata,'$.scope')='global'")
            for scope, key in (("project","project_id"),("type","type_id")):
                if context[key]:
                    scopes.append("(json_extract(i.metadata,'$.scope')=? AND json_extract(i.metadata,'$.scope_id')=?)")
                    args.extend((scope,context[key]))
            clauses.append("("+" OR ".join(scopes or ["0"])+")")
        where = " WHERE "+" AND ".join(clauses) if clauses else ""
        with self.store.db() as db:
            total = db.execute("SELECT count(*) FROM images i"+join+where,args).fetchone()[0]
            rows = db.execute("SELECT i.metadata FROM images i"+join+where+" ORDER BY "+order+" LIMIT ? OFFSET ?",
                              [*args,max(1,min(100,limit)),max(0,offset)]).fetchall()
        items = []
        for row in rows:
            data = json.loads(row[0])
            items.append({k:data[k] for k in ("id","title","category","tags","scope","scope_id","status","width","height","transparent","version")}
                         | {"description":data["description"][:240]})
        return {"items":items,"total":total}

    def preview(self, identifier, context=None):
        # Delivery thumbnail only; original file bytes remain untouched.
        with Image.open(self.path(identifier, context)) as source:
            image = ImageOps.exif_transpose(source).convert("RGBA")
            image.thumbnail((1024,1024))
            output = BytesIO()
            image.save(output,format="PNG")
        return output.getvalue()

    def history(self, identifier):
        self.get(identifier)
        with self.store.db() as db:
            return [{"version":r[0],"author":r[1],"at":r[2],"snapshot":json.loads(r[3])} for r in db.execute(
                "SELECT version,author,at,snapshot FROM image_history WHERE id=? ORDER BY version DESC",(identifier,))]
