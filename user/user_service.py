import os
import requests
from db import init_collection
from jwt_utils import jwt_encode

BOOKING_URL = os.environ.get("BOOKING_URL", "http://localhost:3201")
TIMEOUT = 3

collection = init_collection("users")

NO_ID = {"_id": 0}

class ServiceUnavailableError(Exception):
    """Another service could not be reached."""
    pass

class UpstreamError(Exception):
    """Another service answered with an unexpected error."""
    pass

class NotFoundError(Exception):
    pass

class ConflictError(Exception):
    pass

class ValidationError(Exception):
    pass

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
    return collection.find_one({"id": userid}) is not None

def generate_id(name):
    """Builds an id like 'chris_rivers' from the name, suffixed if already taken."""
    base = name.strip().lower().replace(" ", "_")
    userid, n = base, 1
    while exists(userid):
        userid = f"{base}_{n}"
        n += 1
    return userid

def get_all():
    return list(collection.find({}, NO_ID))

def get_by_id(userid):
    user = collection.find_one({"id": userid}, NO_ID)
    if user is None:
        raise NotFoundError("user not found")
    return user

def login(body):
    if not isinstance(body, dict) or not isinstance(body.get("user_id"), str):
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
    collection.insert_one(dict(user))
    return user

def update_user(userid, body):
    get_by_id(userid)
    validate_fields(body, partial=True)
    fields = {f: body[f] for f in ("name", "last_active") if f in body}
    if fields:
        collection.update_one({"id": userid}, {"$set": fields})
    return get_by_id(userid)

def update_role(userid, role):
    get_by_id(userid)
    if not role:
        raise ValidationError("role must be a non-empty string")
    collection.update_one({"id": userid}, {"$set": { "role": role }})
    return get_by_id(userid)

def delete_user(userid):
    user = get_by_id(userid)
    collection.delete_one({"id": userid})
    return user

def get_user_with_bookings(userid, auth_header):
    """User with detailed bookings (calls Booking, forwards the token); unknown movies get a null title."""
    user = get_by_id(userid)
    query = """query ($id: ID!) {
        booking_with_userid(_userid: $id) { dates { date movies movies_details { id title director rating } } }
    }"""
    try:
        r = requests.post(f"{BOOKING_URL}/graphql", json={"query": query, "variables": {"id": userid}},
                          headers={"Authorization": auth_header or ""}, timeout=TIMEOUT)
    except requests.RequestException:
        raise ServiceUnavailableError("booking service unavailable")
    result = r.json()
    errors = [e["message"] for e in result.get("errors", [])]
    if errors and errors != ["no booking for this user"]:
        raise UpstreamError("booking service error: " + "; ".join(errors))
    booking = (result.get("data") or {}).get("booking_with_userid")
    dates = [{"date": d["date"],
              "movies": [movie or {"id": movieid, "title": None}
                         for movieid, movie in zip(d["movies"], d["movies_details"])]}
             for d in booking["dates"]] if booking else []
    return {**user, "bookings": dates}
