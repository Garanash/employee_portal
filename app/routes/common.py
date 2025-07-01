from fastapi import APIRouter, Depends, HTTPException, Request as StarletteRequest, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..auth import get_current_user
from ..utils import templates

router = APIRouter()

@router.get("/profile", response_class=HTMLResponse)
async def user_profile(
    request: StarletteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse(
        "common/profile.html",
        {"request": request, "user": current_user}
    )