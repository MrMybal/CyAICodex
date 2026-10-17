from .onboarding import setup_guide, Client as GuideClient, Language as GuideLanguage
import asyncio
import base64
import json
import secrets
import sqlite3
from contextlib import asynccontextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations, TextContent, ImageContent
from pydantic import BaseModel, Field

from .assist import CodexLogin, answer, protect
from .store import Conflict, Method, Store
from .startup import startup_enabled, set_startup
from .images import ImageLibrary, ImageDescription, MAX_BYTES
from . import __version__
from .local_clients import client_command, local_status, launch_login, ollama_url
from .mcp_setup import MCPSetup, CLIENTS
from .i18n import language, translate, translated_status, render_index, browser_catalog
from . import connectors
from .updates import Updater

connection_context = ContextVar("connection", default=None)
WEB = Path(__file__).parent / "web"


class SaveRequest(BaseModel):
    method: Method
    version: int | None = None


class ConnectionRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    project_id: str = ""
    type_id: str = ""
    include_global: bool = True
    writable: bool | None = None


class Preferences(BaseModel):
    local_no_token: bool = False
    local_writable: bool = False
    default_writable: bool = False
    project_id: str = ''
    type_id: str = ''
    include_global: bool = True
    codex_path: str = Field(default='', max_length=2000)
    claude_code_path: str = Field(default='', max_length=2000)
    opencode_path: str = Field(default='', max_length=2000)
    ollama_url: str = Field(default='http://127.0.0.1:11434', max_length=2000)


def preferences(store):
    return Preferences.model_validate_json(store.setting('preferences', '{}'))


class GroupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type_id: str | None = None


class SetupRequest(BaseModel):
    without_token: bool = False
    project_id: str = ''
    type_id: str = ''
    include_global: bool = True
    writable: bool = False


class StartupRequest(BaseModel):
    enabled: bool


class UpdateSettings(BaseModel):
    automatic: bool = True
    use_git: bool = False
    token: str = Field(default='', max_length=1000)
    clear_token: bool = False


class LanguageRequest(BaseModel):
    language: Literal['fr', 'en']


class ImageUpdateRequest(BaseModel):
    description: ImageDescription
    version: int


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=30000)


class AssistantRequest(BaseModel):
    provider: Literal["codex", "openai", "claude", "claude_code", "opencode", "ollama",
                      "antigravity", "command_code", "codebuddy", "openrouter", "lmstudio"]
    model: str = Field(default="", max_length=200)
    messages: list[Message] = Field(min_length=1, max_length=30)
    method_ids: list[str] = Field(default_factory=list, max_length=8)
    image_ids: list[str] = Field(default_factory=list, max_length=4)


class ConnectorSettings(BaseModel):
    path: str = Field(default='', max_length=2000)
    url: str = Field(default='', max_length=2000)
    model: str = Field(default='', max_length=200)
    key: str = Field(default='', max_length=1000)
    clear_key: bool = False


class ConnectorTest(BaseModel):
    model: str = Field(default='', max_length=200)


class LocalSecurity:
    def __init__(self, app, store, port):
        self.app, self.store = app, store
        self.hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope["headers"])
        host = headers.get(b"host", b"").decode()
        origin = headers.get(b"origin", b"").decode()
        if host not in self.hosts or (origin and origin not in {"http://"+h for h in self.hosts}):
            return await JSONResponse({"detail": translate("Origine refusée.", language(self.store))}, 403)(scope, receive, send)
        path = scope["path"]
        if path == '/mcp' or path.startswith('/mcp/'):
            auth = headers.get(b"authorization", b"").decode()
            conn = await asyncio.to_thread(self.store.authenticate, auth[7:]) if auth.startswith("Bearer ") else None
            if not auth:
                options = preferences(self.store)
                if options.local_no_token:
                    conn = {**self.store.context(options.project_id, options.type_id, options.include_global),
                            'name':'Accès local sans jeton', 'writable':options.local_writable}
            if not conn:
                return await JSONResponse({"detail": translate("Jeton MCP absent, invalide ou révoqué. Ouvrez CyAICodex > Connexions > Configurer et tester.", language(self.store)), "help": "/mcp-info"}, 401)(scope, receive, send)
            marker = connection_context.set(conn)
            try:
                return await self.app(scope, receive, send)
            finally:
                connection_context.reset(marker)
        if path.startswith("/api/") and path != "/api/session":
            from http.cookies import SimpleCookie
            cookie = SimpleCookie()
            cookie.load(headers.get(b"cookie", b"").decode())
            token = cookie.get("methodes_session")
            if not token or not secrets.compare_digest(token.value, self.store.setting("admin_token")):
                return await JSONResponse({"detail": translate("Ouvrez CyAICodex depuis son icône Windows.", language(self.store))}, 401)(scope, receive, send)
        await self.app(scope, receive, send)


def create_app(folder, port=8765):
    store = Store(folder)
    images = ImageLibrary(store)
    setup = MCPSetup(store, port)
    mcp = FastMCP("CyAICodex", instructions=(
        "For connection/setup questions, call get_setup_guide and explain its steps to the user; never request tokens in chat. "
        "Shared skills library. At the start of a task, call get_context, search_skills, then get_skill. "
        "Respect this connection's scope and write permissions. Save or update skills only when asked; "
        "use expected_version for updates. For images, use search_images, get_image and view_image. "
        "Add images with import_image using a local absolute path or data_base64 and preservation instructions. "
        "Only published resources in scope are visible; an empty list is not a connection failure. "
        "Legacy search_methods/get_method/create_method/update_method remain supported."),
        stateless_http=True, json_response=True, host="127.0.0.1", port=port)

    def ctx():
        value = connection_context.get()
        if value is None:
            raise ValueError("Connexion MCP non authentifiée.")
        return value

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
    def get_context() -> dict[str, Any]:
        """Read this connection's project/type scope and write permissions before looking up methods."""
        c = ctx()
        return {k: c[k] for k in ("name", "project_id", "type_id", "include_global", "writable")}

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
    def get_setup_guide(client: GuideClient = 'all', language: GuideLanguage = 'en') -> dict[str, Any]:
        """Get safe setup instructions to explain to the user. Includes client steps, verification and troubleshooting; never credentials."""
        ctx()
        return setup_guide(client, language, port)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
    def search_methods(query: str = "", category: str = "", limit: int = 10, offset: int = 0) -> dict[str, Any]:
        """Search relevant published methods by keywords (accent-insensitive, prefix, weighted full text).
        Returns concise summaries and IDs; fetch full content with get_method. Empty query lists methods.
        """
        return store.search(query, ctx(), category, limit=limit, offset=offset)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
    def get_method(method_id: str) -> dict[str, Any]:
        """Read a complete method, including its version, only within this connection's scope."""
        return store.get(method_id, ctx())

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False))
    def create_method(method: Method) -> dict[str, Any]:
        """Save a reusable method when asked. Requires a writable connection; scope must match this connection."""
        c = ctx()
        if not c["writable"]:
            raise ValueError("Cette connexion est en lecture seule.")
        return store.save(method, author=c["name"], context=c)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False))
    def update_method(method_id: str, expected_version: int, method: Method) -> dict[str, Any]:
        """Update a method using the version returned by get_method. Conflicts require re-reading, never overwrite blindly."""
        c = ctx()
        if not c["writable"]:
            raise ValueError("Cette connexion est en lecture seule.")
        return store.save(method, method_id, expected_version, c["name"], c)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
    def search_skills(query: str = "", category: str = "", limit: int = 10, offset: int = 0) -> dict[str, Any]:
        """Find published skills in this connection's scope. Read details with get_skill."""
        return search_methods(query, category, limit, offset)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
    def get_skill(skill_id: str) -> dict[str, Any]:
        """Read a skill and its version within this connection's scope."""
        return get_method(skill_id)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False))
    def create_skill(skill: Method) -> dict[str, Any]:
        """Create a skill when requested; requires write access and a matching scope."""
        return create_method(skill)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False))
    def update_skill(skill_id: str, expected_version: int, skill: Method) -> dict[str, Any]:
        """Update a skill with its current version; preserve conflict and access checks."""
        return update_method(skill_id, expected_version, skill)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
    def search_images(query: str = "", limit: int = 10, offset: int = 0) -> dict[str, Any]:
        """Search published visual references and their usage instructions in the connection's project scope."""
        return images.search(query,ctx(),limit=limit,offset=offset)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
    def get_image(image_id: str) -> dict[str, Any]:
        """Read full image description, what to preserve/avoid, usage instructions, and original local file path.
        Use the untouched original for editing; view_image returns a smaller visual preview.
        """
        c = ctx()
        return {**images.get(image_id,c),"original_path":str(images.path(image_id,c).resolve())}

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
    def view_image(image_id: str) -> list[TextContent | ImageContent]:
        """View the image (PNG preview up to 1024px) together with its full preservation instructions."""
        c = ctx()
        return [TextContent(type="text",text=json.dumps(images.get(image_id,c),ensure_ascii=False)),
                ImageContent(type="image",mimeType="image/png",data=base64.b64encode(images.preview(image_id,c)).decode())]

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False))
    def import_image(description: ImageDescription, file_path: str = '', data_base64: str = '') -> dict[str, Any]:
        """Import a NEW image and its detailed preservation instructions into the library.
        Supply exactly one: absolute local file_path (on this Windows PC), or raw data_base64.
        PNG/JPEG/WebP only, up to 20 MB. Requires write access and a matching project scope.
        The original bytes are preserved. Returns the saved image ID and metadata.
        """
        c = ctx()
        if not c['writable']:
            raise ValueError('Cette connexion est en lecture seule.')
        if not store.allowed(description.model_dump(), c):
            raise ValueError('Cette portée n’est pas accessible à la connexion.')
        if bool(file_path) == bool(data_base64):
            raise ValueError('Fournissez soit file_path, soit data_base64, pas les deux.')
        if file_path:
            path = Path(file_path)
            if not path.is_absolute() or str(path).startswith(('\\\\', '//')) or not path.is_file():
                raise ValueError('Indiquez le chemin absolu d’un fichier image local existant.')
            with path.open('rb') as source:
                raw = source.read(MAX_BYTES+1)
        else:
            if len(data_base64) > ((MAX_BYTES+2)//3)*4:
                raise ValueError('Image trop volumineuse (20 Mo maximum).')
            try:
                raw = base64.b64decode(data_base64, validate=True)
            except ValueError:
                raise ValueError('Les données base64 sont invalides.') from None
        return images.add(raw, description, c['name'], c)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False))
    def update_image(image_id: str, expected_version: int, description: ImageDescription) -> dict[str, Any]:
        """Update a visual reference's description and instructions, without changing the original image.
        Requires a writable connection and current version from get_image.
        """
        c = ctx()
        if not c["writable"]:
            raise ValueError("Cette connexion est en lecture seule.")
        return images.update(image_id,description,expected_version,c["name"],c)

    @mcp.resource("methodes://context")
    def context_resource() -> str:
        """Current connection's method scope."""
        return json.dumps(get_context(), ensure_ascii=False)

    @mcp.prompt()
    def appliquer_methodes(task: str) -> str:
        """Start a task consistently with the library's relevant methods."""
        return f"Pour cette tâche : {task}\nConsulte get_context, cherche les skills pertinentes avec search_methods, puis lis-les avec get_method avant de commencer."

    @mcp.resource("skills://context")
    def skills_context_resource() -> str:
        """Current connection's skill scope."""
        return context_resource()

    @mcp.prompt()
    def apply_skills(task: str) -> str:
        """Start a task using applicable skills."""
        return f"Task: {task}\nRead get_context, search_skills and get_skill before starting."

    login = CodexLogin(store)
    updater = Updater(store, port)
    async def watch_updates():
        await asyncio.sleep(15)
        while True:
            if updater.settings()['automatic']:
                await asyncio.to_thread(updater.check)
            await asyncio.sleep(6 * 60 * 60)

    @asynccontextmanager
    async def lifespan(app):
        watcher = asyncio.create_task(watch_updates())
        try:
            async with mcp.session_manager.run():
                yield
        finally:
            watcher.cancel()
            from contextlib import suppress
            with suppress(asyncio.CancelledError):
                await watcher
            await login.close()

    app = FastAPI(title="CyAICodex", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.store = store
    app.state.images = images
    app.state.updater = updater
    app.add_middleware(LocalSecurity, store=store, port=port)

    @app.exception_handler(ValueError)
    async def invalid(request, exc):
        return JSONResponse({"detail": translate(str(exc), language(store))}, 409 if isinstance(exc, Conflict) else 400)

    @app.exception_handler(KeyError)
    async def missing(request, exc):
        return JSONResponse({"detail": translate(str(exc.args[0]), language(store))}, 404)

    @app.exception_handler(sqlite3.IntegrityError)
    async def duplicate(request, exc):
        return JSONResponse({"detail": translate("Ce nom existe déjà ou le groupe choisi est invalide.", language(store))}, 409)

    @app.exception_handler(Exception)
    async def unexpected(request, exc):
        import logging
        logging.exception("Erreur interne")
        return JSONResponse({"detail": translate("Une erreur interne est survenue. Consultez le journal local.", language(store))}, 500)

    @app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers.update({"X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: blob:; connect-src 'self'; frame-ancestors http://127.0.0.1:8766 http://localhost:8766; base-uri 'none'; form-action 'self'",
            "Cache-Control": "no-store"})
        return response

    @app.get("/")
    def index():
        return HTMLResponse(render_index(language(store)))

    @app.get('/static/i18n-data.js')
    def translation_data():
        return Response(browser_catalog(), media_type='application/javascript')

    @app.get('/api/language')
    def get_language():
        return {'language': language(store)}

    @app.put('/api/language')
    def set_language(body: LanguageRequest):
        store.set_setting('ui_language', body.language)
        callback = getattr(app.state, 'language_changed', None)
        if callback:
            callback()
        return {'language': language(store)}

    @app.get("/health")
    def health():
        import sys
        return {"app": "methodes", "status": "ok", "version": __version__,
                "packaged": bool(getattr(sys, "frozen", False)), "tray": getattr(app.state, "tray_active", False)}

    @app.get('/mcp-info')
    def mcp_info():
        return {'name':'CyAICodex','version':__version__,'transport':'Streamable HTTP',
            'url':f'http://127.0.0.1:{port}/mcp','token_required':not preferences(store).local_no_token,
            'setup':'Ouvrez CyAICodex > Connexions > Configurer et tester pour votre client.',
            'workflow':['initialize','tools/list','get_context','search_skills','get_skill'],
            'setup_tool':'get_setup_guide',
            'guides':{lang:f'http://127.0.0.1:{port}/mcp-guide?lang={lang}' for lang in ('en','fr')},
            'clients':['codex','claude_desktop','claude_code','opencode','other'],
            'images':['search_images','get_image','view_image','import_image','update_image'],
            'note':'Un serveur local doit être enregistré dans chaque client IA. Le navigateur seul ne constitue pas un client MCP. Les services cloud ne peuvent pas accéder à ce localhost.'}

    @app.get('/mcp-guide')
    def public_setup_guide(client: GuideClient = 'all', lang: GuideLanguage = 'en'):
        return Response(setup_guide(client, lang, port)['markdown'], media_type='text/markdown',
                        headers={'Content-Disposition': f'attachment; filename="CyAICodex-Setup-{lang}.md"'})

    @app.get('/api/mcp-setup')
    async def setup_status():
        results = await asyncio.gather(*(setup.diagnose(client) for client in CLIENTS))
        return [translated_status(result, language(store)) for result in results]

    @app.get('/api/mcp-setup/{client}')
    async def setup_client_status(client: Literal['codex','claude_desktop','opencode']):
        return translated_status(await setup.diagnose(client), language(store))

    @app.post('/api/mcp-setup/{client}')
    async def setup_client(client: Literal['codex','claude_desktop','opencode'], body: SetupRequest):
        try:
            installed = await asyncio.to_thread(setup.install,client,body.model_dump())
        except OSError:
            raise ValueError('Windows refuse l’écriture de la configuration. Vérifiez les droits du dossier et réessayez. Les autres serveurs sont conservés.') from None
        return {**installed,'diagnostic':translated_status(await setup.diagnose(client), language(store))}

    @app.post("/api/session")
    async def session(request: Request):
        body = await request.json()
        if not secrets.compare_digest(str(body.get("token", "")), store.setting("admin_token")):
            return JSONResponse({"detail": translate("Ouvrez l'application depuis son icône Windows.", language(store))}, 401)
        response = JSONResponse({"ok": True})
        response.set_cookie("methodes_session", store.setting("admin_token"), httponly=True, samesite="strict")
        return response

    @app.get("/api/catalog")
    def catalog():
        return {**store.catalog(), **store.metadata()}

    @app.post("/api/groups/{kind}")
    def group(kind: Literal["types", "projects"], body: GroupRequest):
        return store.add_group(kind, body.name, body.type_id)

    @app.get("/api/methods")
    def methods(q: str = "", project_id: str = "", type_id: str = "", include_global: bool = True,
                category: str = "", status: str = "published", limit: int = 50, offset: int = 0):
        context = store.context(project_id, type_id, include_global) if project_id or type_id else None
        return store.search(q, context, category, status, limit, offset)

    @app.get("/api/methods/{method_id}")
    def method(method_id: str):
        return store.get(method_id)

    @app.post("/api/methods")
    def create(body: SaveRequest):
        return store.save(body.method)

    @app.put("/api/methods/{method_id}")
    def update(method_id: str, body: SaveRequest):
        return store.save(body.method, method_id, body.version)

    @app.get("/api/methods/{method_id}/history")
    def history(method_id: str):
        return store.history(method_id)

    @app.get("/api/connections")
    def connections():
        return store.connections()

    @app.post("/api/connections")
    def connect(body: ConnectionRequest):
        data = body.model_dump()
        if data['writable'] is None:
            data['writable'] = preferences(store).default_writable
        import sys
        root = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent
        return {**store.new_connection(**data), "url": f"http://127.0.0.1:{port}/mcp",
                'bridge_path': str(root/'CyAICodex.exe'), 'command': setup.launch_command()}

    @app.put('/api/connections/{connection_id}')
    async def connection_permissions(connection_id: str, request: Request):
        data = await request.json()
        if not isinstance(data.get('writable'), bool):
            raise ValueError('Le droit d’écriture doit être vrai ou faux.')
        with store.db() as db:
            changed = db.execute('UPDATE connections SET writable=? WHERE id=?', (data['writable'], connection_id))
            if not changed.rowcount:
                raise KeyError('Connexion introuvable.')
        return {'ok':True}

    @app.get('/api/preferences')
    def read_preferences():
        return preferences(store).model_dump()

    @app.put('/api/preferences')
    async def save_preferences(body: Preferences):
        store.context(body.project_id, body.type_id, body.include_global)
        from urllib.parse import urlparse
        url = urlparse(body.ollama_url.rstrip('/'))
        if url.scheme != 'http' or url.hostname not in ('localhost','127.0.0.1','::1') or url.username or url.password or url.path or url.query or url.fragment:
            raise ValueError('L’adresse Ollama doit être une URL HTTP locale sans chemin.')
        for field in ('codex_path','claude_code_path','opencode_path'):
            value = getattr(body, field)
            if value and (not Path(value).is_file() or Path(value).suffix.lower() != '.exe'):
                raise ValueError('Le chemin du client doit désigner un fichier .exe existant.')
        with store.db() as db:
            for key in ('codex_path','claude_code_path','opencode_path','ollama_url'):
                db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)', (key,getattr(body,key)))
            db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)', ('preferences',body.model_dump_json()))
        await login.close()
        return body.model_dump()

    @app.get('/api/local/{provider}/check')
    async def check_local(provider: Literal['codex','claude_code','opencode','ollama']):
        return translated_status(await local_status(provider, store), language(store))

    @app.post('/api/local/{provider}/login')
    def login_local(provider: Literal['claude_code','opencode']):
        launch_login(provider, store)
        return {'ok':True}

    @app.get('/api/connectors')
    def connector_list():
        return [{'id': identifier, **{k: info[k] for k in ('name', 'kind', 'docs', 'images', 'policy')},
                 'config': connectors.configuration(store, identifier),
                 'key_configured': bool(store.setting(identifier + '_key')),
                 'last_test': json.loads(store.setting('connector_test_' + identifier, 'null'))}
                for identifier, info in connectors.CONNECTORS.items()]

    @app.put('/api/connectors/{identifier}')
    def configure_connector(identifier: str, body: ConnectorSettings):
        return connectors.save_configuration(store, identifier, body.model_dump(exclude_unset=True))

    @app.get('/api/connectors/{identifier}/check')
    async def check_connector(identifier: str):
        connectors.descriptor(identifier)
        return translated_status(await connectors.detect(store, identifier), language(store))

    @app.get('/api/connectors/{identifier}/models')
    async def connector_models(identifier: str):
        return {'models': await connectors.models(store, identifier)}

    @app.post('/api/connectors/{identifier}/login')
    def open_connector(identifier: str):
        connectors.launch(store, identifier)
        return {'ok': True}

    @app.post('/api/connectors/{identifier}/test')
    async def test_connector(identifier: str, body: ConnectorTest):
        connectors.descriptor(identifier)
        async with assistant_lock:
            return translated_status(await connectors.test_generation(store, identifier, body.model), language(store))

    @app.delete("/api/connections/{connection_id}")
    def revoke(connection_id: str):
        store.revoke(connection_id)
        return {"ok": True}

    @app.get("/api/export")
    def export():
        return JSONResponse(store.export(), headers={"Content-Disposition": 'attachment; filename="skills.json"'})

    @app.get("/api/images")
    def list_images(q: str = "", project_id: str = "", type_id: str = "", include_global: bool = True,
                    status: str = "published", limit: int = 24, offset: int = 0):
        context = store.context(project_id,type_id,include_global) if project_id or type_id else None
        return images.search(q,context,status,limit,offset)

    @app.post("/api/images")
    async def upload_image(file: UploadFile = File(...), metadata: str = Form(...)):
        try:
            description = ImageDescription.model_validate_json(metadata)
            raw = await file.read(MAX_BYTES+1)
            return await asyncio.to_thread(images.add,raw,description)
        finally:
            await file.close()

    @app.get("/api/images/{image_id}")
    def image_description(image_id: str):
        return images.get(image_id)

    @app.put("/api/images/{image_id}")
    def edit_image_description(image_id: str, body: ImageUpdateRequest):
        return images.update(image_id,body.description,body.version)

    @app.get("/api/images/{image_id}/file")
    def image_file(image_id: str, download: bool = False):
        data = images.get(image_id)
        return FileResponse(images.path(image_id),media_type=data["mime"],
            filename=(image_id+"."+data["extension"]) if download else None)

    @app.get("/api/images/{image_id}/preview")
    def image_preview(image_id: str):
        return Response(images.preview(image_id),media_type="image/png")

    @app.get("/api/images/{image_id}/history")
    def image_history(image_id: str):
        return images.history(image_id)

    @app.get("/api/providers")
    def providers():
        import os
        import shutil
        local = {}
        for name in ('codex','claude_code','opencode'):
            try:
                local[name] = bool(client_command(name, store))
            except ValueError:
                local[name] = False
        return {**local,
                "openai": bool(store.setting("openai_key") or os.environ.get("OPENAI_API_KEY")),
                "claude": bool(store.setting("claude_key") or os.environ.get("ANTHROPIC_API_KEY"))}

    @app.get("/api/startup")
    def read_startup():
        import os
        return {"enabled": startup_enabled(), "supported": os.name == "nt"}

    @app.get('/api/updates')
    def update_status():
        return updater.snapshot()

    @app.put('/api/updates/settings')
    def update_settings(body: UpdateSettings):
        return updater.configure(body.model_dump())

    @app.post('/api/updates/check')
    def check_updates():
        return updater.check()

    @app.post('/api/updates/install')
    def install_update():
        return updater.install()

    @app.put("/api/startup")
    def update_startup(body: StartupRequest):
        try:
            enabled = set_startup(body.enabled, port, store.folder)
        except OSError as exc:
            raise ValueError("Windows a refusé le changement du démarrage automatique.") from exc
        return {"enabled": enabled, "supported": True}

    @app.put("/api/providers/{provider}")
    async def save_key(provider: Literal["openai", "claude"], request: Request):
        data = await request.json()
        key = str(data.get("key", "")).strip()
        if len(key) > 1000:
            raise ValueError("Clé trop longue.")
        store.set_setting(provider+"_key", protect(key) if key else "")
        return {"ok": True}

    @app.post("/api/codex/login")
    async def codex_login():
        return await login.rpc("account/login/start", {"type": "chatgpt"})

    @app.get("/api/codex/account")
    async def codex_account():
        result = await login.rpc("account/read", {"refreshToken": False})
        account = result.get("account")
        return {"connected": bool(account), "type": account.get("type") if account else None}

    assistant_lock = asyncio.Semaphore(2)
    @app.post("/api/assistant")
    async def assistant(body: AssistantRequest):
        async with assistant_lock:
            return {"text": await answer(store, body.provider, body.model,
                        [m.model_dump() for m in body.messages], body.method_ids, body.image_ids)}

    app.mount("/static", StaticFiles(directory=WEB), name="static")
    app.mount("/", mcp.streamable_http_app())
    return app
