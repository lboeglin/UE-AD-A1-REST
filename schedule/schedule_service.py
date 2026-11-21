import json
import os
import requests

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases", "times.json")
MOVIE_URL = os.environ.get("MOVIE_URL", "http://localhost:3200")
TIMEOUT = 3

class ServiceUnavailableError(Exception):
    """Another service could not be reached."""
    pass

class NotFoundError(Exception):
    pass

class ConflictError(Exception):
    pass

class ValidationError(Exception):
    pass

with open(DB_PATH, 'r') as jsf:
    times = json.load(jsf)["schedule"]

def write(times):
    with open(DB_PATH, 'w') as f:
        json.dump({"schedule": times}, f, indent=2)

def validate_fields(body, partial):
    """Raises ValidationError for invalid schedule fields."""
    if not isinstance(body, dict):
        raise ValidationError("body must be a JSON object")
    if not partial and "date" not in body:
        raise ValidationError("'date' is required")
    if "date" in body and (not isinstance(body["date"], str) or not body["date"]):
        raise ValidationError("'date' must be a non-empty string")
    if "movies" not in body:
        raise ValidationError("'movies' is required")
    if not isinstance(body["movies"], list) or not all(isinstance(item, str) for item in body["movies"]):
        raise ValidationError("'movies' must be a list of strings")

def get_all():
    return times

def get_dates_for_movie(movieid):
    return {"movieid": movieid, "dates": [time["date"] for time in times if movieid in time["movies"]]}

def get_by_date(date):
    for time in times:
        if time["date"]==date:
            return time
    raise NotFoundError("time not found")

def add_time(body):
    validate_fields(body, partial=False)
    if any(time["date"] == body["date"] for time in times):
        raise ConflictError("schedule already exists")
    time = {
        "date": body["date"],
        "movies": body["movies"],
    }
    times.append(time)
    write(times)
    return time

def update_movies(date, body):
    time = get_by_date(date)
    validate_fields(body, partial=True)
    time["movies"] = body["movies"]
    write(times)
    return time

def add_movies(date, body):
    time = get_by_date(date)
    validate_fields(body, partial=True)
    for movie in body["movies"]:
        if movie not in time["movies"]:
            time["movies"].append(movie)
    write(times)
    return time

def delete_time(date):
    time = get_by_date(date)
    times.remove(time)
    write(times)
    return time

MOVIE_QUERY = """query ($id: ID!) {
    movie_with_id(id: $id) { id title director rating }
}"""

def get_movies_by_date(date):
    """Schedule of a date with movie details (calls Movie in GraphQL)."""
    time = get_by_date(date)
    movies = []
    try:
        for movieid in time["movies"]:
            r = requests.post(f"{MOVIE_URL}/graphql", json={"query": MOVIE_QUERY, "variables": {"id": movieid}},
                              timeout=TIMEOUT)
            movie = (r.json().get("data") or {}).get("movie_with_id") if r.status_code == 200 else None
            movies.append(movie or {"id": movieid, "title": None})
    except requests.RequestException:
        raise ServiceUnavailableError("movie service unavailable")
    return {"date": date, "movies": movies}
