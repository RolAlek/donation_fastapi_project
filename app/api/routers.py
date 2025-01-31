from fastapi import APIRouter

from api.endpoints import (
    donate_router,
    google_router,
    projects_router,
    users_router,
)

main_router = APIRouter()
main_router.include_router(
    projects_router,
    prefix="/projects",
    tags=["projects"],
)
main_router.include_router(
    donate_router,
    prefix="/donation",
    tags=["donations"],
)
main_router.include_router(users_router)
main_router.include_router(
    google_router,
    prefix="/google",
    tags=["google"],
)
