import booking_service
from jwt_utils import require_admin, require_self_or_admin

@require_admin
def bookings(_, info):
   return booking_service.get_all()

@require_self_or_admin
def booking_with_userid(_, info, _userid):
   return booking_service.get_for_user(_userid)

@require_admin
def bookings_for_movie(_, info, _movieid):
   return booking_service.get_users_for_movie(_movieid)

@require_self_or_admin
def add_booking(_, info, _userid, _date, _movieid):
   return booking_service.add_booking(_userid, _date, _movieid)

@require_self_or_admin
def delete_booking(_, info, _userid, _date, _movieid):
   return booking_service.delete_booking(_userid, _date, _movieid)

def resolve_movies_details(day, info):
   token = info.context["request"].headers.get("Authorization", "")
   return booking_service.get_movies(day["movies"], token)
