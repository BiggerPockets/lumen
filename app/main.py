from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .database import engine, Base
from .routes import auth, events, dashboard, orgs

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lumen", description="Claude Code analytics platform")
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
