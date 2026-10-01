from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound
from user_service import UsersService

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

user_service = UsersService()

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users/<user_id>", methods=['GET'])
def find_by_id(user_id):
   user = user_service.find_by_id(user_id)
   if user is not None:
      return user
   else:
      return make_response(jsonify({"error":"User ID not found"}),500)

@app.route("/users", methods=['GET'])
def find_all():
   return user_service.find_all()

@app.route("/users", methods=['POST'])
def add():
   req = request.get_json()
   return user_service.add(req)

@app.route("/users/<user_id>", methods=['PUT'])
def update(user_id):
   req = request.get_json()
   return user_service.update(user_id,req)

@app.route("/users/<user_id>/<role>", methods=['PUT'])
def update_role(user_id,role):
   return user_service.update_role(user_id,role)

@app.route("/users/<user_id>", methods=['DELETE'])
def delete(user_id):
   return user_service.delete(user_id)


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
