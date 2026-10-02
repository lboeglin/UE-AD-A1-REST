import json
from flask import Flask, render_template, request, jsonify, make_response

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases", "user.json")

class NotFoundError(Exception):
    pass

class ConflictError(Exception):
    pass

class ValidationError(Exception):
    pass

with open(DB_PATH.format("."), 'r') as jsf:
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
    if "last_active" in body and not isinstance(body["last_active"], int):
        raise ValidationError("'last_active' must be an int")
    if "role" in body and (not isinstance(body["role"], str) or not body["role"]):
        raise ValidationError("'role' must be a non-empty string")
    if "id" in body and (isinstance(body["id"], bool) or not isinstance(body["id"], str)):
        raise ValidationError("'id' must be a string")

def get_all():
    return users

def get_by_id(userid):
    for user in users:
        if user["id"]==userid:
            return user
    raise NotFoundError("user not found")

def count_name(name):
    count=0
    for user in users:
        if user["name"] == name:
            count = count+1
    return count

def generate_id(name):
    return name.toLower().replace("", "_")

def add_user(body):
    validate_fields(body, partial=False)
    name = body["name"]
    userid = generate_id(name)
    count = count_name(name)
    if count>0 :
        userid = userid + count
    user = {
        "id": userid,
        "name": body["name"],
        "role": body.get("role", 0),
        "last_active": body.get("last_active", "")
    }
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
    try:
        user["role"] = str(role)
    except ValueError:
        raise ValidationError("role must be a string")
    write(users)
    return user

def delete_user(userid):
    user = get_by_id(userid)
    users.remove(user)
    write(users)
    return user
