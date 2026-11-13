from flask import Flask, request, jsonify, make_response
import booking_service
from booking_service import NotFoundError, ConflictError, ValidationError, ServiceUnavailableError, UpstreamError

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

def error(message, code):
   return make_response(jsonify({"error": message}), code)

@app.errorhandler(NotFoundError)
def handle_not_found(e):
   return error(str(e), 404)

@app.errorhandler(ConflictError)
def handle_conflict(e):
   return error(str(e), 409)

@app.errorhandler(ValidationError)
def handle_validation(e):
   return error(str(e), 400)

@app.errorhandler(ServiceUnavailableError)
def handle_service_unavailable(e):
   return error(str(e), 503)

@app.errorhandler(UpstreamError)
def handle_upstream(e):
   return error(str(e), 502)

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings", methods=['GET'])
def get_bookings():
   return make_response(jsonify(booking_service.get_all()), 200)

@app.route("/bookings/<userid>", methods=['GET'])
def get_booking_for_user(userid):
   return make_response(jsonify(booking_service.get_for_user(userid)), 200)

@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuser(userid):
   booking = booking_service.add_booking(userid, request.get_json(silent=True))
   return make_response(jsonify(booking), 201)

@app.route("/bookings/<userid>/<date>/<movieid>", methods=['DELETE'])
def delete_booking(userid, date, movieid):
   return make_response(jsonify(booking_service.delete_booking(userid, date, movieid)), 200)

@app.route("/bookings/<userid>/movies", methods=['GET'])
def get_booking_movies(userid):
   return make_response(jsonify(booking_service.get_movies_for_user(userid)), 200)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
