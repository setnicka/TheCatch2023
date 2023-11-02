from pydantic import BaseModel, HttpUrl, EmailStr

from typing import Sequence, Optional


class UserBase(BaseModel):
    """
    Utilized for authentication.
    """
    guid: Optional[str]
    email: Optional[EmailStr] = None
    date: Optional[int]
    time_created: Optional[int]
    admin: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    time_created: Optional[int]


# Properties to receive via API on creation
class UserSignup(BaseModel):
    email: EmailStr
    password: str


# Properties to receive via API on creation
class UserPWDchange(BaseModel):
    guid: str
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    ...

class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties stored in DB but not returned by API
class UserInDB(UserInDBBase):
    hashed_password: str


# Additional properties to return via API
class User(UserInDBBase):
    ...

