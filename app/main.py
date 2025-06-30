from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import admin, auth, employee, hr, manager, common
from .config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Portal", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(employee.router, prefix="/employee", tags=["employee"])
app.include_router(manager.router, prefix="/manager", tags=["manager"])
app.include_router(hr.router, prefix="/hr", tags=["hr"])
app.include_router(common.router, tags=["common"])

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    return templates.TemplateResponse("errors/404.html", {"request": request}, status_code=404)

@app.exception_handler(403)
async def forbidden_exception_handler(request: Request, exc):
    return templates.TemplateResponse("errors/403.html", {"request": request}, status_code=403)