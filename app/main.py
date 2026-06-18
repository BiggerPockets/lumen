from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .database import engine, Base
from .routes import auth, events, dashboard, orgs
from .mcp_server import mcp

Base.metadata.create_all(bind=engine)

_mcp_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run the MCP app's lifespan (initializes the StreamableHTTP session manager)
    async with _mcp_app.router.lifespan_context(_mcp_app):
        yield


app = FastAPI(
    title="Lumen",
    description="Claude Code analytics platform",
    lifespan=lifespan,
)
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(dashboard.router)
app.include_router(orgs.router)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return templates.TemplateResponse(request, "index.html", {"base_url": base_url})


@app.get("/health")
def health():
    return {"status": "ok"}


class _MCPASGIMiddleware:
    """Routes /mcp requests directly to FastMCP, bypassing FastAPI's router."""

    def __init__(self, fastapi_app, mcp_asgi_app):
        self._fastapi = fastapi_app
        self._mcp = mcp_asgi_app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope.get("path", "").startswith("/mcp"):
            await self._mcp(scope, receive, send)
        else:
            await self._fastapi(scope, receive, send)


# Wrap at the ASGI level so /mcp bypasses FastAPI's router entirely.
# FastMCP registers its route at /mcp, so the path passes through unchanged.
asgi_app = _MCPASGIMiddleware(app, _mcp_app)
