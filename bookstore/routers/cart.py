from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
import models
from routers.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])
templates = Jinja2Templates(directory="templates")


def get_or_create_cart(user: models.User, db: Session) -> models.Cart:
    cart = db.query(models.Cart).filter(models.Cart.user_id == user.id).first()
    if not cart:
        cart = models.Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def cart_total(cart: models.Cart) -> float:
    return sum(item.book.price * item.quantity for item in cart.items)


def cart_count(cart: models.Cart) -> int:
    return sum(item.quantity for item in cart.items)


@router.get("")
async def view_cart(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login?next=/cart", status_code=302)
    cart = get_or_create_cart(user, db)
    total = cart_total(cart)
    count = cart_count(cart)
    return templates.TemplateResponse("cart.html", {
        "request": request,
        "user": user,
        "cart": cart,
        "total": total,
        "cart_count": count,
        "page": "cart",
    })


@router.post("/add/{book_id}")
async def add_to_cart(
    request: Request,
    book_id: int,
    quantity: int = Form(1),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url=f"/auth/login?next=/books/{book_id}", status_code=302)

    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book or book.stock < 1:
        referer = request.headers.get("referer", "/books")
        return RedirectResponse(url=referer, status_code=302)

    cart = get_or_create_cart(user, db)
    item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id,
        models.CartItem.book_id == book_id,
    ).first()

    if item:
        item.quantity = min(item.quantity + quantity, book.stock)
    else:
        item = models.CartItem(cart_id=cart.id, book_id=book_id, quantity=min(quantity, book.stock))
        db.add(item)

    db.commit()
    referer = request.headers.get("referer", "/books")
    return RedirectResponse(url=referer, status_code=302)


@router.post("/update/{item_id}")
async def update_cart(
    request: Request,
    item_id: int,
    quantity: int = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    item = db.query(models.CartItem).filter(models.CartItem.id == item_id).first()
    if item:
        cart = db.query(models.Cart).filter(models.Cart.id == item.cart_id).first()
        if cart and cart.user_id == user.id:
            if quantity <= 0:
                db.delete(item)
            else:
                item.quantity = min(quantity, item.book.stock)
            db.commit()

    return RedirectResponse(url="/cart", status_code=302)


@router.post("/remove/{item_id}")
async def remove_from_cart(
    request: Request,
    item_id: int,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    item = db.query(models.CartItem).filter(models.CartItem.id == item_id).first()
    if item:
        cart = db.query(models.Cart).filter(models.Cart.id == item.cart_id).first()
        if cart and cart.user_id == user.id:
            db.delete(item)
            db.commit()

    return RedirectResponse(url="/cart", status_code=302)
