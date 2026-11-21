import json
import os
import uuid

import movie_service
from errors import ValidationError, NotFoundError

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases", "actors.json")

with open(DB_PATH, 'r') as jsf:
    actors = json.load(jsf)["actors"]

def write(actors):
    with open(DB_PATH, 'w') as f:
        json.dump({"actors": actors}, f, indent=2)

def validate_fields(body):
    """Raises ValidationError for invalid actors fields."""
    if "firstname" in body and (not isinstance(body["firstname"], str) or not body["firstname"]):
        raise ValidationError("'firstname' must be a non-empty string")

    if "lastname" in body and (not isinstance(body["lastname"], str) or not body["lastname"]):
        raise ValidationError("'lastname' must be a non-empty string")

    if "birthyear" in body and (isinstance(body["birthyear"], bool) or not isinstance(body["birthyear"], int)):
        raise ValidationError("'birthyear' must be a number")
    if "films" in body:
        if not isinstance(body["films"], list) or not all(isinstance(item, str) for item in body["films"]):
            raise ValidationError("'films' must be a list of strings")
        movie_ids = {m["id"] for m in movie_service.get_all()}
        unknown = [f for f in body["films"] if f not in movie_ids]
        if unknown:
            raise ValidationError(f"unknown movie ids in 'films': {unknown}")


def get_all():
    return actors

def get_by_id(actorid):
    actor = next((a for a in actors if a["id"] == actorid), None)
    if actor is None:
        raise NotFoundError("actor not found")
    return actor

def get_by_movie(movieid):
    return [a for a in actors if movieid in a.get("films", [])]

def remove_movie(movieid):
    """Removes movieid from the films of every actor."""
    for actor in get_by_movie(movieid):
        actor["films"].remove(movieid)
    write(actors)

def add_actor(body):
    validate_fields(body)
    actor = {"id": str(uuid.uuid4()),
             "firstname": body["firstname"],
             "lastname": body["lastname"],
             "birthyear": body.get("birthyear", 0),
             "films": body.get("films", [])}
    actors.append(actor)
    write(actors)
    return actor

def update_actor(actorid, body):
    actor = get_by_id(actorid)
    validate_fields(body)
    for field in ("firstname", "lastname", "birthyear", "films"):
        if field in body:
            actor[field] = body[field]
    write(actors)
    return actor

def delete_actor(actorid):
    actor = get_by_id(actorid)
    actors.remove(actor)
    write(actors)
    return actor