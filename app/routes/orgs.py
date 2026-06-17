import re
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import Org

router = APIRouter()


class OrgCreate(BaseModel):
    name: str


@router.post("/orgs", status_code=201)
def create_org(payload: OrgCreate, db: Session = Depends(get_db)):
    slug = re.sub(r"[^a-z0-9]+", "-", payload.name.lower()).strip("-")
    if db.query(Org).filter(Org.slug == slug).first():
        raise HTTPException(status_code=409, detail="Org already exists")
    org = Org(name=payload.name, slug=slug, api_key=secrets.token_urlsafe(32))
    db.add(org)
    db.commit()
    db.refresh(org)
    return {"slug": org.slug, "api_key": org.api_key}
