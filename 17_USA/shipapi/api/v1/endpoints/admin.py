import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Any, Optional

from shipapi import crud
from shipapi import deps

from shipapi import schemas

from shipapi.schemas.admin import GetFile
from shipapi.schemas.user import User
import requests


router = APIRouter()


@router.get("/", status_code=200)
def admin_check(
    *, 
    current_user: User = Depends(deps.parse_token),
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Returns true if the user is in admin role
    """
    if current_user['admin']:
        return {"results": True }

    return {"results": False }


@router.post("/file", status_code=200)
def get_file(
    file_in: GetFile,
    current_user: User = Depends(deps.parse_token),
    db: Session = Depends(deps.get_db)
) -> str:
    """
    Returns a file on the server
    """    
    if not current_user['admin']:
        return {"msg": "Permission Error"}
    try:
        with open(file_in.file) as f:
            output = f.read()
            return {"file": output}
    except:
        raise HTTPException(status_code=404, detail="File not found")

@router.put("/getFlag", status_code=200)
def get_flag(current_user: User = Depends(deps.parse_token)) -> Any:
    """
    The Flag
    """
    if not current_user['admin']:
        return {"msg": "Permission Error"}

    if "flag-read" not in current_user.keys():
        raise HTTPException(status_code=400, detail="flag-read key missing from JWT")

    flag = requests.get('http://flagship:8000').text
    return {"Flag":flag}

