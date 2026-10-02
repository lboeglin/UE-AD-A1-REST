from flask import Flask, request, jsonify, make_response
import movie_service
from movie_service import NotFoundError, ValidationError

app = Flask(__name__)

PORT = 3200
HOST = '0.0.0.0'

def error(message, code):
    return make_response(jsonify({"error": message}), code)

@app.errorhandler(NotFoundError)
def handle_not_found(e):
    return error(str(e), 404)

@app.errorhandler(ValidationError)
def handle_validation(e):
    return error(str(e), 400)

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

@app.route("/json", methods=['GET'])
def get_json():
    return make_response(jsonify(movie_service.get_all()), 200)

@app.route("/movies/<movieid>", methods=['GET'])
def get_movie_byid(movieid):
    return make_response(jsonify(movie_service.get_by_id(movieid)), 200)

@app.route("/moviesbytitle", methods=['GET'])
def get_movie_bytitle():
    return make_response(jsonify(movie_service.get_by_title(request.args.get("title"))), 200)

@app.route("/movies", methods=['POST'])
def add_movie():
    movie = movie_service.add_movie(request.get_json(silent=True))
    return make_response(jsonify(movie), 201)

@app.route("/movies/<movieid>", methods=['PUT'])
def update_movie(movieid):
    movie = movie_service.update_movie(movieid, request.get_json(silent=True))
    return make_response(jsonify(movie), 200)

@app.route("/movies/<movieid>/<rate>", methods=['PUT'])
def update_movie_rating(movieid, rate):
    return make_response(jsonify(movie_service.update_rating(movieid, rate)), 200)

@app.route("/movies/<movieid>", methods=['DELETE'])
def delete_movie(movieid):
    return make_response(jsonify(movie_service.delete_movie(movieid)), 200)

if __name__ == "__main__":
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)
