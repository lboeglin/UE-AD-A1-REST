import base64
import hashlib
import hmac
import json
import os
import time
from functools import wraps

from flask import request

from errors import UnauthorizedError, ForbiddenError

SECRET = os.environ.get("JWT_SECRET", "ohnothereisnosecret")

def b64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def b64url_decode(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

def sign(message):
    return b64url_encode(hmac.new(SECRET.encode(), message.encode(), hashlib.sha256).digest())

def jwt_decode(token):
    """Returns the payload, or raises ValueError if the token is invalid or expired."""
    try:
        header, body, signature = token.split(".")
    except ValueError:
        raise ValueError("malformed token")
    if not hmac.compare_digest(sign(f"{header}.{body}"), signature):
        raise ValueError("invalid token")
    payload = json.loads(b64url_decode(body))
    if payload.get("exp", 0) < time.time():
        raise ValueError("token expired")
    return payload

def payload_from_request():
    """Reads 'Authorization: Bearer <token>' and returns the verified payload (raises ValueError)."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise ValueError("missing token")
    return jwt_decode(auth[len("Bearer "):])

def require_admin(f):
    """Route decorator: requires 'Authorization: Bearer <token>' with role 'admin'."""
    @wraps(f)
    def wrapper(obj, info,*args, **kwargs):
        try:
            payload = payload_from_request()
        except ValueError as e:
            raise UnauthorizedError(str(e))
        if payload.get("role") != "admin":
            raise ForbiddenError("admin role required")
        return f(obj, info, *args, **kwargs)
    return wrapper