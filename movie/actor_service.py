import uuid
import movie_service
from db import init_collection
from errors import ValidationError, NotFoundError

collection = init_collection("actors")

NO_ID = {"_id": 0}

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
    return list(collection.find({}, NO_ID))

def get_by_id(actorid):
    actor = collection.find_one({"id": actorid}, NO_ID)
    if actor is None:
        raise NotFoundError("actor not found")
    return actor

def get_by_movie(movieid):
    return list(collection.find({"films": movieid}, NO_ID))

def remove_movie(movieid):
    """Removes movieid from the films of every actor."""
    collection.update_many({"films": movieid}, {"$pull": {"films": movieid}})

def add_actor(body):
    validate_fields(body)
    actor = {"id": str(uuid.uuid4()),
             "firstname": body["firstname"],
             "lastname": body["lastname"],
             "birthyear": body.get("birthyear", 0),
             "films": body.get("films", [])}
    collection.insert_one(dict(actor))
    return actor

def update_actor(actorid, body):
    get_by_id(actorid)
    validate_fields(body)
    fields = {f: body[f] for f in ("firstname", "lastname", "birthyear", "films") if f in body}
    if fields:
        collection.update_one({"id": actorid}, {"$set": fields})
    return get_by_id(actorid)

def delete_actor(actorid):
    actor = get_by_id(actorid)
    collection.delete_one({"id": actorid})
    return actor
