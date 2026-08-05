from pwdlib import PasswordHash
from jwt import encode, decode
from config import app_settings
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

NoAccess_Exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid ID",
    )


password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password=password, hash=hashed_password)


def create_access_token(payload):
    #encoded = jwt.encode({"some": "payload"}, key, algorithm="HS256")

    exp = datetime.now(tz=timezone.utc) + timedelta(minutes=app_settings.access_token_expire_minutes)
    payload.update({"exp": exp})
    access_token = encode(payload=payload, key=app_settings.jwt_secret, algorithm=app_settings.jwt_algorithm)
    return access_token

def get_current_user(token: str = Depends(oauth2_scheme)):
    #jwt.decode(encoded, key, algorithms="HS256")
    credentials_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail= "User could not be authorised",
        headers= {"WWW-Authenticate": "Bearer"})
    try:
        payload = decode(jwt=token, key=app_settings.jwt_secret, algorithms=[app_settings.jwt_algorithm])
        user_id:int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    return {"sub": int(payload["sub"])}
