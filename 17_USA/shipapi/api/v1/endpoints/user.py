from typing import Any, Annotated
from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from shipapi import crud
from shipapi import schemas
from shipapi import deps
from shipapi.models.user import User
from shipapi.core.security import get_password_hash

from shipapi.core.auth import (
    authenticate,
    create_access_token,
)

router = APIRouter()

@router.get("/{user_id}", status_code=200, response_model=schemas.User)
def fetch_user(*,
               user_id: int,
               db: Session = Depends(deps.get_db),
               current_user: User = Depends(deps.parse_token)
               ) -> Any:
    """
    Fetch a user by ID
    """
    result = crud.user.get(db=db, id=user_id)
    return result

@router.post("/signup", summary="Create User Account", status_code=201)
async def create_user_signup(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.user.UserSignup,
) -> Any:
    """
    Create new user
    """

    new_user = schemas.user.UserCreate(**user_in.dict())

    new_user.guid = str(uuid4())

    user = db.query(User).filter(User.email == new_user.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user = crud.user.create(db=db, obj_in=new_user)

    return user

@router.post("/login", summary="User Login", response_model=schemas.Token)
async def login(request: Request,
                form_data: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(deps.get_db)
                ) -> Any:
    """
    Logs in the user and returns JWT
    """

    timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    user = authenticate(email=form_data.username, password=form_data.password, db=db)
    if not user:
        with open("auth.log", "a") as f:
            f.write(f"{timestamp} - Login Failure for {form_data.username} - {request.client.host}\n")
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    with open("auth.log", "a") as f:
        f.write(f"{timestamp} - Login Success for {form_data.username} - {request.client.host}\n")

    return {
        "access_token": create_access_token(sub=user.id, admin=user.admin, guid=user.guid),
        "token_type": "bearer",
    }

@router.post("/updatepassword", response_model=schemas.User, summary="Update User Password", status_code=201)
async def update_password(
        *,
        current_user: User = Depends(deps.parse_token),
        db: Session = Depends(deps.get_db),
        user_in: schemas.user.UserPWDchange,
) -> Any:
    """
    Update a user password
    """

    user = db.query(User).filter(User.guid == user_in.guid).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Cannot find user",
        )
    user_in.password
    crud.user.update(db=db, db_obj=user, obj_in=user_in)
    return user

