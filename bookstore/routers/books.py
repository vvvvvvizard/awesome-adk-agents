from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
import models
from routers.auth import get_current_user

router = APIRouter(tags=["books"])
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    featured = db.query(models.Book).filter(models.Book.featured == True).limit(8).all()  # noqa: E712
    bestsellers = db.query(models.Book).filter(models.Book.bestseller == True).limit(6).all()  # noqa: E712
    new_arrivals = db.query(models.Book).filter(models.Book.new_arrival == True).limit(4).all()  # noqa: E712
    categories = db.query(models.Category).all()
    cart_count = _cart_count(request, db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "featured": featured,
        "bestsellers": bestsellers,
        "new_arrivals": new_arrivals,
        "categories": categories,
        "cart_count": cart_count,
        "page": "home",
    })


@router.get("/books")
async def catalog(
    request: Request,
    db: Session = Depends(get_db),
    category: str = Query(None),
    search: str = Query(None),
    sort: str = Query("featured"),
    min_price: float = Query(None),
    max_price: float = Query(None),
    page: int = Query(1, ge=1),
):
    user = get_current_user(request, db)
    categories = db.query(models.Category).all()
    query = db.query(models.Book)

    if category:
        cat = db.query(models.Category).filter(models.Category.slug == category).first()
        if cat:
            query = query.filter(models.Book.category_id == cat.id)

    if search:
        query = query.filter(
            or_(
                models.Book.title.ilike(f"%{search}%"),
                models.Book.author.ilike(f"%{search}%"),
                models.Book.description.ilike(f"%{search}%"),
            )
        )

    if min_price is not None:
        query = query.filter(models.Book.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Book.price <= max_price)

    sort_options = {
        "price_asc": models.Book.price.asc(),
        "price_desc": models.Book.price.desc(),
        "rating": models.Book.rating.desc(),
        "newest": models.Book.id.desc(),
        "title": models.Book.title.asc(),
    }
    order = sort_options.get(sort, models.Book.featured.desc())
    query = query.order_by(order)

    per_page = 12
    total = query.count()
    books = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page

    cart_count = _cart_count(request, db)

    return templates.TemplateResponse("catalog.html", {
        "request": request,
        "user": user,
        "books": books,
        "categories": categories,
        "selected_category": category,
        "search": search,
        "sort": sort,
        "min_price": min_price,
        "max_price": max_price,
        "page": page,
        "total_pages": total_pages,
        "total": total,
        "cart_count": cart_count,
        "current_page": "catalog",
    })


@router.get("/books/{book_id}")
async def book_detail(request: Request, book_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        return templates.TemplateResponse("404.html", {"request": request, "user": user}, status_code=404)

    reviews = db.query(models.Review).filter(models.Review.book_id == book_id).all()
    related = (
        db.query(models.Book)
        .filter(models.Book.category_id == book.category_id, models.Book.id != book_id)
        .limit(4)
        .all()
    )
    user_review = None
    if user:
        user_review = db.query(models.Review).filter(
            models.Review.user_id == user.id,
            models.Review.book_id == book_id,
        ).first()

    cart_count = _cart_count(request, db)
    return templates.TemplateResponse("book_detail.html", {
        "request": request,
        "user": user,
        "book": book,
        "reviews": reviews,
        "related": related,
        "user_review": user_review,
        "cart_count": cart_count,
        "page": "catalog",
    })


@router.post("/books/{book_id}/review")
async def add_review(
    request: Request,
    book_id: int,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url=f"/auth/login?next=/books/{book_id}", status_code=302)

    form = await request.form()
    rating = int(form.get("rating", 5))
    comment = form.get("comment", "")

    existing = db.query(models.Review).filter(
        models.Review.user_id == user.id,
        models.Review.book_id == book_id,
    ).first()

    if existing:
        existing.rating = rating
        existing.comment = comment
    else:
        review = models.Review(user_id=user.id, book_id=book_id, rating=rating, comment=comment)
        db.add(review)

    if not existing:
        all_reviews = db.query(models.Review).filter(models.Review.book_id == book_id).all()
        book = db.query(models.Book).filter(models.Book.id == book_id).first()
        if book and all_reviews:
            book.rating = sum(r.rating for r in all_reviews) / len(all_reviews)
            book.review_count = len(all_reviews)

    db.commit()
    return RedirectResponse(url=f"/books/{book_id}", status_code=302)


def _cart_count(request: Request, db: Session) -> int:
    user_id = request.session.get("user_id")
    if not user_id:
        return 0
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart:
        return 0
    return sum(item.quantity for item in cart.items)
