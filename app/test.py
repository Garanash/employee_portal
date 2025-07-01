from fastapi import FastAPI
from app.database import SessionLocal
from app.models import User, UserRole
from app.auth import get_password_hash

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

def create_test_users():
    db = SessionLocal()
    users = [
        User(
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=get_password_hash("admin123"),
            department="IT",
            position="Administrator",
            role=UserRole.ADMIN,
            is_active=True
        ),
        User(
            email="hr@example.com",
            full_name="HR User",
            hashed_password=get_password_hash("hr123"),
            department="HR",
            position="HR Specialist",
            role=UserRole.HR,
            is_active=True
        ),
        User(
            email="manager@example.com",
            full_name="Manager User",
            hashed_password=get_password_hash("manager123"),
            department="Sales",
            position="Manager",
            role=UserRole.MANAGER,
            is_active=True
        ),
        User(
            email="employee@example.com",
            full_name="Employee User",
            hashed_password=get_password_hash("employee123"),
            department="Support",
            position="Employee",
            role=UserRole.EMPLOYEE,
            is_active=True
        ),
    ]
    for user in users:
        existing = db.query(User).filter(User.email == user.email).first()
        if not existing:
            db.add(user)
    db.commit()
    db.close()
    print("Test users created.")

if __name__ == "__main__":
    create_test_users()
