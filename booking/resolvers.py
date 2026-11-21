import booking_service
from jwt_utils import check_admin, check_self_or_admin

def bookings(_, info):
   check_admin(info.context["request"])
   return booking_service.get_all()

def booking_with_userid(_, info, _userid):
   check_self_or_admin(info.context["request"], _userid)
   return booking_service.get_for_user(_userid)

def bookings_for_movie(_, info, _movieid):
   check_admin(info.context["request"])
   return booking_service.get_users_for_movie(_movieid)

def add_booking(_, info, _userid, _date, _movieid):
   check_self_or_admin(info.context["request"], _userid)
   return booking_service.add_booking(_userid, _date, _movieid)

def delete_booking(_, info, _userid, _date, _movieid):
   check_self_or_admin(info.context["request"], _userid)
   return booking_service.delete_booking(_userid, _date, _movieid)

def resolve_movies_details(day, info):
   token = info.context["request"].headers.get("Authorization", "")
   return [booking_service.get_movie(movieid, token) for movieid in day["movies"]]
