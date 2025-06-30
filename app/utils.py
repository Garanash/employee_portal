from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import models

templates = Jinja2Templates(directory="app/templates")

def render_template(
    request: Request,
    template_name: str,
    context: dict = {},
    status_code: int = 200
) -> HTMLResponse:
    context.update({"request": request})
    return templates.TemplateResponse(
        template_name,
        context,
        status_code=status_code
    )

def get_user_dashboard_route(user: models.User):
    if user.role == models.UserRole.ADMIN:
        return "/admin/dashboard"
    elif user.role == models.UserRole.HR:
        return "/hr/dashboard"
    elif user.role == models.UserRole.MANAGER:
        return "/manager/dashboard"
    else:
        return "/employee/dashboard"