import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases", "times.json")

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
    if "movies" in body and not isinstance(body["movies"], list) and all(isinstance(item,str) for item in body["movies"] or not body["movies"]):
        raise ValidationError("'movies' must be a list of strings")

def get_all():
    return times

def get_by_date(date):
    for time in times:
        if time["date"]==date:
            return time
    raise NotFoundError("time not found")

def add_time(body):
    validate_fields(body, partial=False)
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
    try:
        for movie in body["movies"]:
            if movie in time["movies"]:
                pass
            else:
                time["movies"].append(movie)
    except ValueError:
        raise ValidationError("movie must be a string")
    write(times)
    return time

def delete_time(date):
    time = get_by_date(date)
    times.remove(time)
    write(times)
    return time
