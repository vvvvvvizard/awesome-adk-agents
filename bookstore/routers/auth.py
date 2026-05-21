from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
import models

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(models.User).filter(models.User.id == user_id).first()


@router.get("/login")
async def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "user": None,
        "error": None,
        "page": "login",
    })


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "user": None,
            "error": "Invalid email or password.",
            "page": "login",
        })
    request.session["user_id"] = user.id
    next_url = request.query_params.get("next", "/")
    return RedirectResponse(url=next_url, status_code=302)


@router.get("/register")
async def register_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("register.html", {
        "request": request,
        "user": None,
        "error": None,
        "page": "register",
    })


@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "user": None,
            "error": "Passwords do not match.",
            "page": "register",
        })

    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "user": None,
            "error": "An account with this email already exists.",
            "page": "register",
        })

    if len(password) < 6:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "user": None,
            "error": "Password must be at least 6 characters.",
            "page": "register",
        })

    new_user = models.User(
        name=name,
        email=email,
        hashed_password=pwd_context.hash(password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    request.session["user_id"] = new_user.id
    return RedirectResponse(url="/", status_code=302)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)


@router.get("/profile")
async def profile_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login?next=/auth/profile", status_code=302)
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "page": "profile",
        "success": None,
        "error": None,
    })


@router.post("/profile")
async def update_profile(
    request: Request,
    name: str = Form(...),
    phone: str = Form(""),
    address: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    user.name = name
    user.phone = phone
    user.address = address
    db.commit()
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "page": "profile",
        "success": "Profile updated successfully!",
        "error": None,
    })
