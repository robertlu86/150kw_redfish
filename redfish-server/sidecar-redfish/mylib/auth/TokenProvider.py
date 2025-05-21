'''
Python Requirements:
    PyJWT==2.10.1

Usage:
    Step1: Add following variable in .bashrc
        ```
        ITG_JWT_SECRET_KEY="secret" # for dev
        ```
    Step2: Restart your terminal
'''

import os
import jwt
import time
import uuid
from typing import List, Dict

SECRET_KEY = os.environ.get("ITG_JWT_SECRET_KEY", "secret")
ALGORITHM = "HS256"
TOKEN_TTL = 3600  # 1 小時

class TokenProvider:
    @staticmethod
    def issue_token(username: str, role: str, privileges: List[str]) -> str:
        now = int(time.time())
        payload = {
            "sub": username,
            "role": role,
            "privileges": privileges,
            "iat": now,
            "exp": now + TOKEN_TTL,
            "jti": str(uuid.uuid4())
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired.")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token.")

    @staticmethod
    def verify_privilege(token: str, required: str) -> bool:
        payload = TokenProvider.decode_token(token)
        return required in payload.get("privileges", [])