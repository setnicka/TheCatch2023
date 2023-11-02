from typing import Optional, MutableMapping, List, Union
from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm.session import Session
from jose import jwt

from shipapi.models.user import User
from shipapi.appconfig.config import settings
from shipapi.core.security import verify_password


JWTPayloadMapping = MutableMapping[
    str, Union[datetime, bool, str, List[str], List[int]]
]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/user/login")


def authenticate(
    *,
    email: str,
    password: str,
    db: Session,
) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(*, 
    sub: str,
    guid: str,
    admin: bool
) -> str:
    return _create_token(
        token_type="access_token",
        lifetime=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        sub=sub,
        guid=guid,
        admin=admin
    )


def _create_token(
    token_type: str,
    lifetime: timedelta,
    sub: str,
    guid: str,
    admin: bool
) -> str:
    payload = {}
    expire = datetime.utcnow() + lifetime
    payload["type"] = token_type


    payload["exp"] = expire

    # The "iat" (issued at) claim identifies the time at which the
    # JWT was issued.
    payload["iat"] = datetime.utcnow()

    payload["sub"] = str(sub)
    payload["admin"] = bool(admin)
    payload["guid"] = str(guid)
    return jwt.encode(payload, settings.JWT_RSA_KEY, algorithm=settings.ALGORITHM)

