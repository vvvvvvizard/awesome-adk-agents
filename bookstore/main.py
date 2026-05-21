import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from database import engine
import models
from routers import auth, books, cart, orders
import seed_data

models.Base.metadata.create_all(bind=engine)
seed_data.seed()

app = FastAPI(title="PageTurner Bookstore", version="1.0.0")

SECRET_KEY = os.environ.get("SECRET_KEY", "bookstore-super-secret-key-change-in-prod-2024")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=86400 * 7)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(cart.router)
app.include_router(orders.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
