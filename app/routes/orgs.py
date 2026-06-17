import os
import re
import secrets
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import Org

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

ADMIN_SECRET = os.environ.get("ADMIN_SECRET")


class OrgCreate(BaseModel):
    name: str


# JSON API endpoint (used by curl / programmatic clients)
@router.post("/orgs", status_code=201)
def create_org(payload: OrgCreate, db: Session = Depends(get_db)):
    return _create_org(payload.name, db)


# Browser setup page
@router.get("/setup", response_class=HTMLResponse)
def setup_page(request: Request):
    return templates.TemplateResponse(
        request, "setup.html", {"admin_secret_required": bool(ADMIN_SECRET)}
    )


@router.post("/setup", response_class=HTMLResponse)
def setup_submit(
    request: Request,
    name: str = Form(...),
    admin_secret: str = Form(""),
    db: Session = Depends(get_db),
):
    if ADMIN_SECRET and admin_secret.strip() != ADMIN_SECRET:
        return templates.TemplateResponse(
            request,
            "setup.html",
            {"admin_secret_required": True, "error": "Invalid admin secret."},
        )
    try:
        org = _create_org(name.strip(), db)
    except HTTPException as e:
        return templates.TemplateResponse(
            request,
            "setup.html",
            {"admin_secret_required": bool(ADMIN_SECRET), "error": e.detail},
        )
    return templates.TemplateResponse(
        request, "setup.html", {"admin_secret_required": bool(ADMIN_SECRET), "created": org}
    )


def _create_org(name: str, db: Session) -> dict:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if db.query(Org).filter(Org.slug == slug).first():
        raise HTTPException(status_code=409, detail="An org with that name already exists.")
    org = Org(name=name, slug=slug, api_key=secrets.token_urlsafe(32))
    db.add(org)
    db.commit()
    db.refresh(org)
    return {"slug": org.slug, "api_key": org.api_key}
