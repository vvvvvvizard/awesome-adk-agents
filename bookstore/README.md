# PageTurner Bookstore 📚

A fully functional ecommerce website for a bookstore, built with FastAPI, SQLAlchemy, and Jinja2 templates styled with Tailwind CSS.

## Features

- **Book Catalog** — Browse 21 seed books across 8 categories (Fiction, Sci-Fi, Mystery, Fantasy, Self-Help, Biography, Non-Fiction, Children's)
- **Search & Filter** — Full-text search by title/author, filter by category and price range, sort by rating/price/newest
- **Book Detail Pages** — Cover image, description, metadata, related books, customer reviews
- **User Accounts** — Register, login, update profile (bcrypt-hashed passwords, session cookies)
- **Shopping Cart** — Add/update/remove items, free shipping threshold indicator
- **Checkout** — Shipping form, multiple payment methods (card, PayPal, COD)
- **Order History** — View all orders with status, detailed order view with progress tracker
- **Customer Reviews** — Star rating + comment system for authenticated users

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Database | SQLite via SQLAlchemy ORM |
| Templates | Jinja2 server-side rendering |
| Styling | Tailwind CSS (CDN) + custom CSS |
| Auth | Session middleware (itsdangerous) + passlib/bcrypt |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
python main.py
# → http://localhost:8080
```

## Demo Account

| Email | Password |
|-------|----------|
| demo@bookstore.com | demo1234 |

## Project Structure

```
bookstore/
├── main.py              # FastAPI app entry point + middleware
├── database.py          # SQLAlchemy engine & session
├── models.py            # ORM models (Book, Category, User, Cart, Order, Review)
├── seed_data.py         # 21 sample books across 8 categories
├── requirements.txt
├── routers/
│   ├── auth.py          # Login, register, logout, profile
│   ├── books.py         # Home, catalog, book detail, reviews
│   ├── cart.py          # Cart CRUD
│   └── orders.py        # Checkout, order history, order detail
├── templates/
│   ├── base.html        # Navbar, footer, announcement bar
│   ├── index.html       # Homepage (hero, featured, bestsellers, new arrivals)
│   ├── catalog.html     # Browse with sidebar filters + pagination
│   ├── book_detail.html # Book page with add-to-cart, reviews
│   ├── cart.html        # Cart with quantity controls
│   ├── checkout.html    # Checkout with shipping + payment form
│   ├── order_confirmation.html
│   ├── orders.html      # Order history list
│   ├── order_detail.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   └── partials/book_card.html
└── static/
    ├── css/style.css
    └── js/main.js
```
