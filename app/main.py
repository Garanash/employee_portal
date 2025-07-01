from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import engine, Base
from .routes import admin, auth, employee, hr, manager, common

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(employee.router, prefix="/employee", tags=["employee"])
app.include_router(manager.router, prefix="/manager", tags=["manager"])
app.include_router(hr.router, prefix="/hr", tags=["hr"])
app.include_router(common.router, tags=["common"])

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request, "user": None})

# Для запуска приложения используйте одну из команд:
#   uvicorn app.main:app --reload
# или
#   python app/main.py
#
# Запускать из корня проекта (где находится папка app)
#
# Убедитесь, что все зависимости установлены: pip install -r requirements.txt

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)