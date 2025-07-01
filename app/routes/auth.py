from fastapi import APIRouter, Depends, HTTPException, Request as StarletteRequest, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from ..models import User
from ..schemas import Token, UserCreate
from ..auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)
from ..config import settings
from ..utils import templates, get_user_dashboard_route

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: StarletteRequest):
    return templates.TemplateResponse("auth/login.html", {"request": request, "user": None})


@router.post("/login")
async def login(
        request: StarletteRequest,
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Invalid email or password", "user": None},
            status_code=401
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    response = RedirectResponse(url=get_user_dashboard_route(user), status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False,  # Set to True in production with HTTPS
        path="/"
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: StarletteRequest):
    return templates.TemplateResponse("auth/register.html", {"request": request, "user": None})


@router.post("/register")
async def register(
        request: StarletteRequest,
        email: str = Form(...),
        full_name: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        department: str = Form(...),
        position: str = Form(...),
        db: Session = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Passwords do not match", "user": None},
            status_code=400
        )

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Email already registered", "user": None},
            status_code=400
        )

    hashed_password = get_password_hash(password)
    new_user = User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        department=department,
        position=position,
        role="employee"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/auth/login", status_code=303)