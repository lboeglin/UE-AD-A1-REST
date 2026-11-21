import requests
import json
import os

SCHEDULE_URL = os.environ.get("SCHEDULE_URL", "http://localhost:3202")
MOVIE_URL = os.environ.get("MOVIE_URL", "http://localhost:3200")
USER_URL = os.environ.get("USER_URL", "http://localhost:3203")
TIMEOUT = 3
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases", "bookings.json")

class NotFoundError(Exception):
   pass

class ConflictError(Exception):
   pass

class ValidationError(Exception):
   pass

class ServiceUnavailableError(Exception):
   """Another service could not be reached."""
   pass

class UpstreamError(Exception):
   """Another service answered with an unexpected error."""
   pass

with open(DB_PATH, "r") as jsf:
   bookings = json.load(jsf)["bookings"]

def write(bookings):
   with open(DB_PATH, "w") as f:
      json.dump({"bookings": bookings}, f, indent=2)

def find_booking(userid):
   return next((b for b in bookings if b["userid"] == userid), None)

def get_all():
   return bookings

def get_for_user(userid):
   booking = find_booking(userid)
   if booking is None:
      raise NotFoundError("no booking for this user")
   return booking

def check_scheduled(date, movieid):
   """Raises ValidationError unless the Schedule service lists movieid on date."""
   try:
      r = requests.get(f"{SCHEDULE_URL}/times/{date}", timeout=TIMEOUT)
   except requests.RequestException:
      raise ServiceUnavailableError("schedule service unavailable")
   if r.status_code == 404 or (r.status_code == 200 and movieid not in r.json()["movies"]):
      raise ValidationError("this movie is not scheduled on this date")
   if r.status_code != 200:
      raise UpstreamError("schedule service error")

def add_booking(userid, date, movieid):
   check_scheduled(date, movieid)

   booking = find_booking(userid)
   if booking is None:
      booking = {"userid": userid, "dates": []}
      bookings.append(booking)
   day = next((d for d in booking["dates"] if d["date"] == date), None)
   if day is None:
      day = {"date": date, "movies": []}
      booking["dates"].append(day)
   if movieid in day["movies"]:
      raise ConflictError("this booking already exists")
   day["movies"].append(movieid)
   write(bookings)
   return booking

def delete_booking(userid, date, movieid):
   booking = find_booking(userid)
   day = booking and next((d for d in booking["dates"] if d["date"] == date), None)
   if not day or movieid not in day["movies"]:
      raise NotFoundError("booking not found")
   day["movies"].remove(movieid)
   if not day["movies"]:
      booking["dates"].remove(day)
   if not booking["dates"]:
      bookings.remove(booking)
   write(bookings)
   return {"userid": userid, "date": date, "movieid": movieid}

MOVIE_QUERY = """query ($id: String!) {
   movie_with_id(_id: $id) { id title director rating }
}"""

def get_movie(movieid, auth_header):
   try:
      r = requests.post(f"{MOVIE_URL}/graphql", json={"query": MOVIE_QUERY, "variables": {"id": movieid}},
                        headers={"Authorization": auth_header}, timeout=TIMEOUT)
   except requests.RequestException:
      raise ServiceUnavailableError("movie service unavailable")
   movie = (r.json().get("data") or {}).get("movie_with_id") if r.status_code == 200 else None
   return movie or {"id": movieid, "title": None}

def get_users_for_movie(movieid):
   """Who booked movieid and when, with user names (calls User)."""
   found = [(b["userid"], d["date"]) for b in bookings for d in b["dates"] if movieid in d["movies"]]
   names = {}
   try:
      for userid, _ in found:
         if userid not in names:
            r = requests.get(f"{USER_URL}/users/{userid}", timeout=TIMEOUT)
            names[userid] = r.json()["name"] if r.status_code == 200 else None
   except requests.RequestException:
      raise ServiceUnavailableError("user service unavailable")
   return {"movieid": movieid,
           "bookings": [{"userid": u, "name": names[u], "date": d} for u, d in found]}
