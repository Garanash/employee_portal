from .admin import router as admin_router
from .auth import router as auth_router
from .employee import router as employee_router
from .hr import router as hr_router
from .manager import router as manager_router
from .common import router as common_router

__all__ = [
    "admin_router",
    "auth_router",
    "employee_router",
    "hr_router",
    "manager_router",
    "common_router"
]