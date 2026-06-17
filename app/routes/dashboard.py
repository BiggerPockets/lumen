from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from ..database import get_db
from ..models import Event, Org
from .auth import get_current_org, COOKIE_NAME

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    org = get_current_org(request, db)
    if not org:
        return RedirectResponse(url="/login", status_code=303)
    since = datetime.now(timezone.utc) - timedelta(days=30)

    total = db.query(func.count(Event.id)).filter(Event.org_id == org.id).scalar() or 0

    unique_users = (
        db.query(func.count(func.distinct(Event.user)))
        .filter(Event.org_id == org.id, Event.user.isnot(None))
        .scalar() or 0
    )

    unique_projects = (
        db.query(func.count(func.distinct(Event.project)))
        .filter(Event.org_id == org.id, Event.project.isnot(None))
        .scalar() or 0
    )

    events_by_type = (
        db.query(Event.event, func.count(Event.id).label("count"))
        .filter(Event.org_id == org.id)
        .group_by(Event.event)
        .order_by(desc("count"))
        .all()
    )

    daily_counts = (
        db.query(func.date(Event.timestamp).label("date"), func.count(Event.id).label("count"))
        .filter(Event.org_id == org.id, Event.timestamp >= since)
        .group_by(func.date(Event.timestamp))
        .order_by(func.date(Event.timestamp))
        .all()
    )

    top_users = (
        db.query(Event.user, func.count(Event.id).label("count"))
        .filter(Event.org_id == org.id, Event.user.isnot(None))
        .group_by(Event.user)
        .order_by(desc("count"))
        .limit(8)
        .all()
    )

    top_projects = (
        db.query(Event.project, func.count(Event.id).label("count"))
        .filter(Event.org_id == org.id, Event.project.isnot(None))
        .group_by(Event.project)
        .order_by(desc("count"))
        .limit(8)
        .all()
    )

    recent = (
        db.query(Event)
        .filter(Event.org_id == org.id)
        .order_by(desc(Event.created_at))
        .limit(25)
        .all()
    )

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "org": org,
            "total": total,
            "unique_users": unique_users,
            "unique_projects": unique_projects,
            "events_by_type": events_by_type,
            "daily_labels": [str(r.date) for r in daily_counts],
            "daily_data": [r.count for r in daily_counts],
            "top_users": top_users,
            "top_projects": top_projects,
            "recent": recent,
        },
    )
