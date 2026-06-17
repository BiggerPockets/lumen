from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .database import engine, Base
from .routes import events, dashboard, orgs

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lumen", description="Claude Code analytics platform")

app.include_router(events.router)
app.include_router(dashboard.router)
app.include_router(orgs.router)


@app.get("/health")
def health():
    return {"status": "ok"}
