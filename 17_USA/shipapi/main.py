import asyncio

from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi_contrib.common.responses import UJSONResponse
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from typing import Optional, Any
from pathlib import Path
from sqlalchemy.orm import Session

from shipapi.schemas.user import User
from shipapi.api.v1.api import api_router
from shipapi.appconfig.config import settings

from shipapi import deps
from shipapi import crud

app = FastAPI(title="Naval ship API", openapi_url=None, docs_url=None, redoc_url=None)
root_router = APIRouter(default_response_class=UJSONResponse)


@app.get("/", summary=" ", status_code=200, include_in_schema=False)
def root():
    """
    Root
    """
    return {"msg": "Naval ship API version 1.0"}


@app.get("/api", summary="List versions", status_code=200, include_in_schema=False)
def list_versions():
    """
    API versions
    """
    return {"endpoints": ["v1"]}


@app.get("/api/v1", summary="List v1 endpoints", status_code=200, include_in_schema=False)
def list_endpoints_v1():
    """
    API v1 Endpoints
    """
    return {"endpoints": ["user", "admin"]}


@app.get("/docs", summary="Documentation", include_in_schema=False)
async def get_documentation(
        current_user: User = Depends(deps.parse_token)
):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Naval ship API docs")


@app.get("/openapi.json", include_in_schema=False)
async def openapi(
        current_user: User = Depends(deps.parse_token)
):
    return get_openapi(title="Naval Ship API", version="1.0", routes=app.routes)


app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(root_router)


def start():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80, log_level="debug")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80, log_level="debug")

