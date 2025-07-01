from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import User, Request, RequestStatus, RequestType
from ..auth import get_current_user
from ..utils import render_template

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse, response_model=Request)
async def employee_dashboard(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    pending_requests = db.query(Request).filter(
        Request.owner_id == current_user.id,
        Request.status.in_([RequestStatus.PENDING, RequestStatus.APPROVED])
    ).count()

    return render_template(
        request,
        "employee/dashboard.html",
        {
            "user": current_user,
            "pending_requests": pending_requests
        }
    )


@router.get("/requests", response_class=HTMLResponse, response_model=Request)
async def list_requests(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    requests = db.query(Request).filter(
        Request.owner_id == current_user.id
    ).order_by(Request.created_at.desc()).all()

    return render_template(
        request,
        "employee/requests.html",
        {
            "user": current_user,
            "requests": requests,
            "RequestStatus": RequestStatus
        }
    )


@router.get("/requests/new", response_class=HTMLResponse, response_model=Request)
async def create_request_form(
        request: Request,
        current_user: User = Depends(get_current_user)
):
    return render_template(
        request,
        "employee/create_request.html",
        {
            "user": current_user,
            "types": [type.value for type in RequestType]
        }
    )


@router.post("/requests/new")
async def create_request(
        request: Request,
        request_type: str = Form(...),
        content: str = Form(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    new_request = Request(
        type=request_type,
        content=content,
        status=RequestStatus.DRAFT,
        owner_id=current_user.id,
        manager_id=current_user.manager_id
    )

    db.add(new_request)
    db.commit()

    return RedirectResponse(url="/employee/requests", status_code=303)


@router.get("/requests/{request_id}", response_class=HTMLResponse, response_model=Request)
async def request_detail(
        request: Request,
        request_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    request_obj = db.query(Request).filter(
        Request.id == request_id,
        Request.owner_id == current_user.id
    ).first()

    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found")

    return render_template(
        request,
        "employee/request_detail.html",
        {
            "user": current_user,
            "req": request_obj,
            "RequestStatus": RequestStatus
        }
    )


@router.get("/requests/{request_id}/edit", response_class=HTMLResponse, response_model=Request)
async def edit_request_form(
        request: Request,
        request_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    request_obj = db.query(Request).filter(
        Request.id == request_id,
        Request.owner_id == current_user.id,
        Request.status == RequestStatus.DRAFT
    ).first()

    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found or cannot be edited")

    return render_template(
        request,
        "employee/edit_request.html",
        {
            "user": current_user,
            "req": request_obj,
            "types": [type.value for type in RequestType]
        }
    )


@router.post("/requests/{request_id}/edit")
async def update_request(
        request: Request,
        request_id: int,
        request_type: str = Form(...),
        content: str = Form(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    request_obj = db.query(Request).filter(
        Request.id == request_id,
        Request.owner_id == current_user.id,
        Request.status == RequestStatus.DRAFT
    ).first()

    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found or cannot be edited")

    request_obj.type = request_type
    request_obj.content = content
    db.commit()

    return RedirectResponse(url=f"/employee/requests/{request_id}", status_code=303)


@router.post("/requests/{request_id}/submit", response_model=Request)
async def submit_request(
        request: Request,
        request_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    request_obj = db.query(Request).filter(
        Request.id == request_id,
        Request.owner_id == current_user.id,
        Request.status == RequestStatus.DRAFT
    ).first()

    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found or cannot be submitted")

    request_obj.status = RequestStatus.PENDING
    request_obj.updated_at = datetime.utcnow()
    db.commit()

    return RedirectResponse(url=f"/employee/requests/{request_id}", status_code=303)


@router.post("/requests/{request_id}/delete", response_model=Request)
async def delete_request(
        request: Request,
        request_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    request_obj = db.query(Request).filter(
        Request.id == request_id,
        Request.owner_id == current_user.id,
        Request.status == RequestStatus.DRAFT
    ).first()

    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found or cannot be deleted")

    db.delete(request_obj)
    db.commit()

    return RedirectResponse(url="/employee/requests", status_code=303)