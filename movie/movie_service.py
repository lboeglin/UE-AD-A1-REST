import json
import os
import uuid

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases", "movies.json")

class NotFoundError(Exception):
    pass

class ValidationError(Exception):
    pass

with open(DB_PATH, 'r') as jsf:
    movies = json.load(jsf)["movies"]

def write(movies):
    with open(DB_PATH, 'w') as f:
        json.dump({"movies": movies}, f, indent=2)

def validate_fields(body, partial):
    """Raises ValidationError for invalid movie fields."""
    if not isinstance(body, dict):
        raise ValidationError("body must be a JSON object")
    if not partial and "title" not in body:
        raise ValidationError("'title' is required")
    if "title" in body and (not isinstance(body["title"], str) or not body["title"]):
        raise ValidationError("'title' must be a non-empty string")
    if "director" in body and not isinstance(body["director"], str):
        raise ValidationError("'director' must be a string")
    if "rating" in body and (isinstance(body["rating"], bool) or not isinstance(body["rating"], (int, float))):
        raise ValidationError("'rating' must be a number")

def get_all():
    return movies

def get_by_id(movieid):
    movie = next((m for m in movies if m["id"] == movieid), None)
    if movie is None:
        raise NotFoundError("movie not found")
    return movie

def get_by_title(title):
    if not title:
        raise ValidationError("missing 'title' query parameter")
    movie = next((m for m in movies if m["title"] == title), None)
    if movie is None:
        raise NotFoundError("movie not found")
    return movie

def add_movie(body):
    validate_fields(body, partial=False)
    movie = {"id": str(uuid.uuid4()), "title": body["title"],
             "rating": body.get("rating", 0), "director": body.get("director", "")}
    movies.append(movie)
    write(movies)
    return movie

def update_movie(movieid, body):
    movie = get_by_id(movieid)
    validate_fields(body, partial=True)
    for field in ("title", "rating", "director"):
        if field in body:
            movie[field] = body[field]
    write(movies)
    return movie

def update_rating(movieid, rate):
    movie = get_by_id(movieid)
    try:
        movie["rating"] = float(rate)
    except ValueError:
        raise ValidationError("rate must be a number")
    write(movies)
    return movie

def delete_movie(movieid):
    movie = get_by_id(movieid)
    movies.remove(movie)
    write(movies)
    return movie
