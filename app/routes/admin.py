from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserRole
from ..auth import get_current_user, check_admin
from ..utils import render_template

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse, response_model=Request)
async def admin_dashboard(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    check_admin(current_user)

    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()

    return render_template(
        request,
        "admin/dashboard.html",
        {
            "user": current_user,
            "total_users": total_users,
            "active_users": active_users
        }
    )


@router.get("/users", response_class=HTMLResponse, response_model=Request)
async def list_users(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    check_admin(current_user)

    users = db.query(User).all()
    return render_template(
        request,
        "admin/users.html",
        {"user": current_user, "users": users}
    )


@router.get("/users/{user_id}", response_class=HTMLResponse, response_model=Request)
async def user_detail(
        request: Request,
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    check_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    managers = db.query(User).filter(User.role == UserRole.MANAGER).all()

    return render_template(
        request,
        "admin/user_detail.html",
        {
            "user": current_user,
            "target_user": user,
            "managers": managers,
            "roles": [role.value for role in UserRole]
        }
    )


@router.post("/users/{user_id}/update")
async def update_user(
        request: Request,
        user_id: int,
        full_name: str = Form(...),
        email: str = Form(...),
        department: str = Form(...),
        position: str = Form(...),
        role: str = Form(...),
        is_active: str = Form("off"),
        manager_id: str = Form(None),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    check_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.full_name = full_name
    user.email = email
    user.department = department
    user.position = position
    user.role = role
    user.is_active = is_active == "on"
    user.manager_id = int(manager_id) if manager_id else None

    db.commit()

    return RedirectResponse(url=f"/admin/users/{user_id}", status_code=303)


@router.post("/users/{user_id}/delete", response_model=Request)
async def delete_user(
        request: Request,
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    check_admin(current_user)

    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return RedirectResponse(url="/admin/users", status_code=303)