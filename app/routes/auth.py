from fastapi import APIRouter, Depends, HTTPException, Request, Form
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
from ..utils import render_template, get_user_dashboard_route

router = APIRouter()


@router.get("/login", response_class=HTMLResponse, response_model=Request)
async def login_page(request: Request):
    return render_template(request, "auth/login.html")


@router.post("/login")
async def login(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, email, password)
    if not user:
        return render_template(
            request,
            "auth/login.html",
            {"error": "Invalid email or password"},
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
    )
    return response


@router.get("/logout", response_model=Request)
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/register", response_class=HTMLResponse, response_model=Request)
async def register_page(request: Request):
    return render_template(request, "auth/register.html")


@router.post("/register")
async def register(
        request: Request,
        email: str = Form(...),
        full_name: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        department: str = Form(...),
        position: str = Form(...),
        db: Session = Depends(get_db)
):
    if password != confirm_password:
        return render_template(
            request,
            "auth/register.html",
            {"error": "Passwords do not match"},
            status_code=400
        )

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return render_template(
            request,
            "auth/register.html",
            {"error": "Email already registered"},
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