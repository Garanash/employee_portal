from fastapi import Request as StarletteRequest
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import models
from typing import Optional
import traceback

templates = Jinja2Templates(directory="app/templates")

def render_template(
    request: StarletteRequest,
    template_name: str,
    context: Optional[dict] = None,
    status_code: int = 200
) -> HTMLResponse:
    if context is None:
        context = {}
    context.update({"request": request})
    try:
        return templates.TemplateResponse(
            template_name,
            context,
            status_code=status_code
        )
    except Exception as e:
        print('Jinja2 error:', e)
        traceback.print_exc()
        return HTMLResponse(f"<pre>{traceback.format_exc()}</pre>", status_code=500)

def get_user_dashboard_route(user: models.User):
    if user.role == models.UserRole.ADMIN:
        return "/admin/dashboard"
    elif user.role == models.UserRole.HR:
        return "/hr/dashboard"
    elif user.role == models.UserRole.MANAGER:
        return "/manager/dashboard"
    else:
        return "/employee/dashboard"