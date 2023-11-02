from fastapi import APIRouter

from shipapi.api.v1.endpoints import user, admin


api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])



