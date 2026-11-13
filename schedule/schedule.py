from flask import Flask, request, jsonify, make_response

import schedule_service
from schedule_service import ValidationError, NotFoundError, ConflictError

app = Flask(__name__)

PORT = 3202
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

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the schedule service!</h1>"

@app.route("/json", methods=['GET'])
def get_json():
    return make_response(jsonify(schedule_service.get_all()), 200)

@app.route("/times/<date>", methods=['GET'])
def get_time_bydate(date):
    return make_response(jsonify(schedule_service.get_by_date(date)), 200)

@app.route("/times", methods=['POST'])
def add_time():
    req = request.get_json()
    return schedule_service.add_time(req)

@app.route("/times/<date>", methods=['POST'])
def add_movies(date):
    req = request.get_json()
    return schedule_service.add_movies(date,req)

@app.route("/times/<date>", methods=['PUT'])
def update_movies(date):
    req = request.get_json()
    return schedule_service.update_movies(date,req)


@app.route("/times/<date>", methods=['DELETE'])
def delete_times(date):
    return schedule_service.delete_time(date)


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
