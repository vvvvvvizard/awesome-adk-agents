from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
import models
from routers.auth import get_current_user
from routers.cart import get_or_create_cart, cart_total, cart_count

router = APIRouter(prefix="/orders", tags=["orders"])
templates = Jinja2Templates(directory="templates")


@router.get("/checkout")
async def checkout_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login?next=/orders/checkout", status_code=302)

    cart = get_or_create_cart(user, db)
    if not cart.items:
        return RedirectResponse(url="/cart", status_code=302)

    total = cart_total(cart)
    count = cart_count(cart)
    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "user": user,
        "cart": cart,
        "total": total,
        "shipping": 4.99 if total < 35 else 0,
        "cart_count": count,
        "page": "checkout",
        "error": None,
    })


@router.post("/checkout")
async def place_order(
    request: Request,
    shipping_name: str = Form(...),
    shipping_email: str = Form(...),
    shipping_phone: str = Form(""),
    shipping_address: str = Form(...),
    payment_method: str = Form("card"),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    cart = get_or_create_cart(user, db)
    if not cart.items:
        return RedirectResponse(url="/cart", status_code=302)

    total = cart_total(cart)
    shipping_cost = 4.99 if total < 35 else 0.0
    grand_total = total + shipping_cost

    order = models.Order(
        user_id=user.id,
        total=grand_total,
        shipping_name=shipping_name,
        shipping_email=shipping_email,
        shipping_phone=shipping_phone,
        shipping_address=shipping_address,
        payment_method=payment_method,
        status="confirmed",
    )
    db.add(order)
    db.flush()

    for item in cart.items:
        order_item = models.OrderItem(
            order_id=order.id,
            book_id=item.book_id,
            quantity=item.quantity,
            price=item.book.price,
        )
        db.add(order_item)
        book = db.query(models.Book).filter(models.Book.id == item.book_id).first()
        if book:
            book.stock = max(0, book.stock - item.quantity)

    for item in list(cart.items):
        db.delete(item)

    db.commit()
    return RedirectResponse(url=f"/orders/{order.id}/confirmation", status_code=302)


@router.get("/{order_id}/confirmation")
async def order_confirmation(request: Request, order_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == user.id,
    ).first()
    if not order:
        return RedirectResponse(url="/", status_code=302)

    cart_count_val = 0
    return templates.TemplateResponse("order_confirmation.html", {
        "request": request,
        "user": user,
        "order": order,
        "cart_count": cart_count_val,
        "page": "orders",
    })


@router.get("")
async def order_history(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login?next=/orders", status_code=302)

    orders = (
        db.query(models.Order)
        .filter(models.Order.user_id == user.id)
        .order_by(models.Order.created_at.desc())
        .all()
    )
    cart = get_or_create_cart(user, db)
    count = cart_count(cart)
    return templates.TemplateResponse("orders.html", {
        "request": request,
        "user": user,
        "orders": orders,
        "cart_count": count,
        "page": "orders",
    })


@router.get("/{order_id}")
async def order_detail(request: Request, order_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == user.id,
    ).first()
    if not order:
        return RedirectResponse(url="/orders", status_code=302)

    cart = get_or_create_cart(user, db)
    count = cart_count(cart)
    return templates.TemplateResponse("order_detail.html", {
        "request": request,
        "user": user,
        "order": order,
        "cart_count": count,
        "page": "orders",
    })
