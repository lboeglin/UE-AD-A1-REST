import json
import os
from jwt_utils import jwt_encode

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases", "users.json")

class NotFoundError(Exception):
    pass

class ConflictError(Exception):
    pass

class ValidationError(Exception):
    pass

with open(DB_PATH, 'r') as jsf:
    users = json.load(jsf)["users"]

def write(users):
    with open(DB_PATH, 'w') as f:
        json.dump({"users": users}, f, indent=2)

def validate_fields(body, partial):
    """Raises ValidationError for invalid user fields."""
    if not isinstance(body, dict):
        raise ValidationError("body must be a JSON object")
    if not partial and "name" not in body:
        raise ValidationError("'name' is required")
    if "name" in body and (not isinstance(body["name"], str) or not body["name"]):
        raise ValidationError("'name' must be a non-empty string")
    if "last_active" in body and (isinstance(body["last_active"], bool) or not isinstance(body["last_active"], int)):
        raise ValidationError("'last_active' must be an int")
    if "role" in body and (not isinstance(body["role"], str) or not body["role"]):
        raise ValidationError("'role' must be a non-empty string")
    if "id" in body and (not isinstance(body["id"], str) or not body["id"]):
        raise ValidationError("'id' must be a non-empty string")

def exists(userid):
    return any(u["id"] == userid for u in users)

def generate_id(name):
    """Builds an id like 'chris_rivers' from the name, suffixed if already taken."""
    base = name.strip().lower().replace(" ", "_")
    userid, n = base, 1
    while exists(userid):
        userid = f"{base}_{n}"
        n += 1
    return userid

def get_all():
    return users

def get_by_id(userid):
    user = next((u for u in users if u["id"] == userid), None)
    if user is None:
        raise NotFoundError("user not found")
    return user

def login(body):
    if not isinstance(body, dict) or "user_id" not in body:
        raise ValidationError("'user_id' is required")
    user = get_by_id(body["user_id"])
    return {"token": jwt_encode({"sub": user["id"], "role": user["role"]})}

def add_user(body):
    validate_fields(body, partial=False)
    if "id" in body:
        if exists(body["id"]):
            raise ConflictError("user ID already exists")
        userid = body["id"]
    else:
        userid = generate_id(body["name"])
    user = {"id": userid, "name": body["name"],
            "last_active": body.get("last_active", 0), "role": body.get("role", "user")}
    users.append(user)
    write(users)
    return user

def update_user(userid, body):
    user = get_by_id(userid)
    validate_fields(body, partial=True)
    for field in ("name", "last_active"):
        if field in body:
            user[field] = body[field]
    write(users)
    return user

def update_role(userid, role):
    user = get_by_id(userid)
    if not role:
        raise ValidationError("role must be a non-empty string")
    user["role"] = role
    write(users)
    return user

def delete_user(userid):
    user = get_by_id(userid)
    users.remove(user)
    write(users)
    return user
