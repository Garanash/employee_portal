from fastapi import APIRouter, Depends, HTTPException, Request as StarletteRequest, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import User, Request, RequestStatus
from ..auth import get_current_user, check_manager
from ..utils import render_template

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def manager_dashboard(
        request: StarletteRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    check_manager(current_user)

    pending_count = db.query(Request).filter(
        Request.manager_id == current_user.id,
        Request.status == RequestStatus.PENDING
    ).count()

    approved_count = db.query(Request).filter(
        Request.manager_id == current_user.id,
        Request.status == RequestStatus.APPROVED
    ).count()

    return render_template(
        request,
        "manager/dashboard.html",
        {
            "user": current_user,
            "pending_count": pending_count,
            "approved_count": approved_count
        }
    )


@router.get("/requests", response_class=HTMLResponse)
async def list_requests(
        request: StarletteRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    check_manager(current_user)

    requests = db.query(Request).filter(
        Request.manager_id == current_user.id,
        Request.status.in_([RequestStatus.PENDING, RequestStatus.APPROVED, RequestStatus.REJECTED])
    ).order_by(Request.created_at.desc()).all()

    return render_template(
        request,
        "manager/requests.html",
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
    check_manager(current_user)

    request_obj = db.query(Request).filter(
        Request.id == request_id,
        Request.manager_id == current_user.id
    ).first()

    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found")

    return render_template(
        request,
        "manager/request_detail.html",
        {
            "user": current_user,
            "req": request_obj,
            "RequestStatus": RequestStatus
        }
    )


@router.post("/requests/{request_id}/approve")
async def approve_request(
        request: StarletteRequest,
        request_id: int,
        comment: str = Form(None),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    check_manager(current_user)

    request_obj = db.query(Request).filter(
        Request.id == request_id,
        Request.manager_id == current_user.id,
        Request.status == RequestStatus.PENDING
    ).first()

    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found or cannot be approved")

    request_obj.status = RequestStatus.APPROVED
    request_obj.manager_comment = comment
    request_obj.updated_at = datetime.utcnow()
    db.commit()

    return RedirectResponse(url=f"/manager/requests/{request_id}", status_code=303)


@router.post("/requests/{request_id}/reject")
async def reject_request(
        request: StarletteRequest,
        request_id: int,
        comment: str = Form(None),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    check_manager(current_user)

    request_obj = db.query(Request).filter(
        Request.id == request_id,
        Request.manager_id == current_user.id,
        Request.status == RequestStatus.PENDING
    ).first()

    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found or cannot be rejected")

    request_obj.status = RequestStatus.REJECTED
    request_obj.manager_comment = comment
    request_obj.updated_at = datetime.utcnow()
    db.commit()

    return RedirectResponse(url=f"/manager/requests/{request_id}", status_code=303)