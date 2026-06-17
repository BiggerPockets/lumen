import os
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Org

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

COOKIE_NAME = "lumen_session"


def get_current_org(request: Request, db: Session = Depends(get_db)):
    api_key = request.cookies.get(COOKIE_NAME)
    if not api_key:
        return None
    return db.query(Org).filter(Org.api_key == api_key).first()


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


@router.post("/login")
def login(request: Request, api_key: str = Form(...), db: Session = Depends(get_db)):
    org = db.query(Org).filter(Org.api_key == api_key.strip()).first()
    if not org:
        return templates.TemplateResponse(
            request, "login.html", {"error": "Invalid API key."}
        )
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(COOKIE_NAME, api_key.strip(), httponly=True, samesite="lax")
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response
