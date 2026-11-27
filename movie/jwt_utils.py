import base64
import hashlib
import hmac
import json
import os
import time
from functools import wraps

SECRET = os.environ.get("JWT_SECRET", "ohnothereisnosecret")

class AuthenticationError(PermissionError):
    pass

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

def token_payload(req):
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise AuthenticationError("missing token")
    try:
        return jwt_decode(auth[len("Bearer "):])
    except ValueError as e:
        raise AuthenticationError(str(e))

def require_admin(resolver):
    @wraps(resolver)
    def wrapper(obj, info, **kwargs):
        payload = token_payload(info.context["request"])
        if payload.get("role") != "admin":
            raise PermissionError("admin role required")
        return resolver(obj, info, **kwargs)
    return wrapper

def require_self_or_admin(resolver):
    @wraps(resolver)
    def wrapper(obj, info, **kwargs):
        payload = token_payload(info.context["request"])
        if payload.get("role") != "admin" and payload.get("sub") != kwargs["_userid"]:
            raise PermissionError("forbidden")
        return resolver(obj, info, **kwargs)
    return wrapper
