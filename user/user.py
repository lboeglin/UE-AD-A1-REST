from flask import Flask, render_template, request, jsonify, make_response
import user_service
from werkzeug.exceptions import NotFound
from user_service import NotFoundError, ConflictError, ValidationError

app = Flask(__name__)

PORT = 3203
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
   return make_response("<h1 style='color:blue'>Welcome to the User service!</h1>",200)

@app.route("/json", methods=['GET'])
def get_json():
   return make_response(jsonify(user_service.get_all()), 200)

@app.route("/users/<user_id>", methods=['GET'])
def get_user_byid(movieid):
   return make_response(jsonify(user_service.get_by_id(movieid)), 200)

@app.route("/users", methods=['POST'])
def add_user():
   req = request.get_json()
   return user_service.add(req)

@app.route("/users/<user_id>", methods=['PUT'])
def update_user(user_id):
   req = request.get_json()
   return user_service.update(user_id,req)

@app.route("/users/<user_id>/<role>", methods=['PUT'])
def update_user_role(user_id,role):
   return user_service.update_role(user_id,role)

@app.route("/users/<user_id>", methods=['DELETE'])
def delete_user(user_id):
   return user_service.delete(user_id)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
