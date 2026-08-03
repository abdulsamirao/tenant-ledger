from pwdlib import PasswordHash
from PyJWT


password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password=password, hash=hashed_password)


def create_access_token(dict):
    #encoded = jwt.encode({"some": "payload"}, key, algorithm="HS256")

def decode_access_token(token):
    #jwt.decode(encoded, key, algorithms="HS256")
