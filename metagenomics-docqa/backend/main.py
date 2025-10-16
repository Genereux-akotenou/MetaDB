from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from .database import init_database
from . import auth as auth_router
from .routers import upload as upload_router
from .routers import review as review_router
from .routers import provider as provider_router


def create_app() -> FastAPI:
    app = FastAPI(title="MetaDB DocQA Platform")

    # CORS for frontend usage
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup static files and templates
    base_dir = os.path.dirname(os.path.dirname(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "static")), name="static")
    templates = Jinja2Templates(directory=os.path.join(frontend_dir, "templates"))

    init_database()

    # API routes
    app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
    app.include_router(upload_router.router, prefix="/upload", tags=["upload"])
    app.include_router(review_router.router, prefix="/review", tags=["review"])
    app.include_router(provider_router.router, prefix="/provider", tags=["provider"])

    # Frontend routes
    @app.get("/", response_class=HTMLResponse)
    async def login_page(request: Request):
        return templates.TemplateResponse("login.html", {"request": request})

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard_page(request: Request):
        return templates.TemplateResponse("dashboard.html", {"request": request})

    return app


app = create_app()


