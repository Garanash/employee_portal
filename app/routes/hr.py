from fastapi import APIRouter, Depends, HTTPException, Request as StarletteRequest, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import User, Request, RequestStatus
from ..auth import get_current_user, check_hr
from ..utils import render_template

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def hr_dashboard(
        request: StarletteRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    check_hr(current_user)

    pending_count = db.query(Request).filter(
        Request.status == RequestStatus.APPROVED
    ).count()

    completed_count = db.query(Request).filter(
        Request.status == RequestStatus.COMPLETED
    ).count()

    return render_template(
        request,
        "hr/dashboard.html",
        {
            "user": current_user,
            "pending_count": pending_count,
            "completed_count": completed_count
        }
    )


@router.get("/requests", response_class=HTMLResponse)
async def list_requests(
        request: StarletteRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    check_hr(current_user)

    requests = db.query(Request).filter(
        Request.status.in_([RequestStatus.APPROVED, RequestStatus.COMPLETED])
    ).order_by(Request.created_at.desc()).all()

    return render_template(
        request,
        "hr/requests.html",
        {
            "user": current_user,
            "requests": requests,
            "RequestStatus": RequestStatus
        }
    )


@router.get("/requests/{request_id}", response_class=HTMLResponse)
async def request_detail(
        request: StarletteRequest,
        request_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    check_hr(current_user)

    request_obj = db.query(Request).filter(
        Request.id == request_id,
        Request.status.in_([RequestStatus.APPROVED, RequestStatus.COMPLETED])
    ).first()

    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found")

    return render_template(
        request,
        "hr/request_detail.html",
        {
            "user": current_user,
            "req": request_obj,
            "RequestStatus": RequestStatus
        }
    )


@router.get("/requests/{request_id}/process", response_class=HTMLResponse)
async def process_request_form(
        request: StarletteRequest,
        request_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    check_hr(current_user)

    request_obj = db.query(Request).filter(
        Request.id == request_id,
        Request.status == RequestStatus.APPROVED
    ).first()

    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found or cannot be processed")

    return render_template(
        request,
        "hr/process_request.html",
        {
            "user": current_user,
            "req": request_obj
        }
    )


@router.post("/requests/{request_id}/complete")
async def complete_request(
        request: StarletteRequest,
        request_id: int,
        comment: str = Form(None),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    check_hr(current_user)

    request_obj = db.query(Request).filter(
        Request.id == request_id,
        Request.status == RequestStatus.APPROVED
    ).first()

    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found or cannot be completed")

    request_obj.status = RequestStatus.COMPLETED
    request_obj.hr_officer_id = current_user.id
    request_obj.hr_comment = comment
    request_obj.updated_at = datetime.utcnow()
    db.commit()

    return RedirectResponse(url=f"/hr/requests/{request_id}", status_code=303)