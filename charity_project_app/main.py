from fastapi import FastAPI

from charity_project_app.api import main_router
from charity_project_app.core import db_manager
from charity_project_app.core.config import settings
from charity_project_app.core.init_superuser import create_first_superuser

main_app = FastAPI(
    title=settings.app_title,
)

main_app.include_router(main_router, prefix="/api")


@main_app.on_event("startup")
async def startup_event():
    await create_first_superuser()


@main_app.on_event("shutdown")
async def shutdown_event():
    await db_manager.dispose()
