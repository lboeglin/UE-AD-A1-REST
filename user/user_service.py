import json
from flask import Flask, render_template, request, jsonify, make_response

with open('{}/databases/users.json'.format("."), 'r') as jsf:
    users = json.load(jsf)["users"]

class UsersService:

    def __init__(self):
        pass

    def write(self,users):
        with open('{}/databases/users.json'.format("."), 'w') as f:
            full = {}
            full['users']=users
            json.dump(full, f)

    def find_by_id(
            self,
            id
    ):
        for user in users:
            if user["id"]==id:
                return user
        return None

    def find_all(self):
        return make_response(jsonify(users), 200)

    def delete(
            self,
            id
    ):
        user = self.find_by_id(id)
        if user is not None:
            users.remove(user)
            self.write(users)
            return make_response(jsonify({"success":"user was removed"}),200)
        return make_response(jsonify({"error":"user ID does not exists"}),500)

    def add(
            self,
            json
    ):
        id = json["id"]
        user = self.find_by_id(id)
        if user is not None:
            return make_response(jsonify({"error":"user ID already exists"}),500)
        users.append(json)
        self.write(users)
        return make_response(jsonify({"success":"user was created"}),200)

    def update(
            self,
            id,
            json
    ):
        user = self.find_by_id(id)
        if user is None:
            return make_response(jsonify({"error":"user ID does not exist"}),500)
        if json["name"] is not None:
            user["name"] = json["name"]
        if json["last_active"] is not None:
            user["last_active"] = json["last_active"]
        self.write(users)
        return make_response(jsonify({"success":"user was updated"}),200)

    def update_role(
            self,
            id,
            role
    ):
        user = self.find_by_id(id)
        if user is None:
            return make_response(jsonify({"error":"user ID does not exist"}),500)
        user["role"] = role
        self.write(users)
        return make_response(jsonify({"success":"user's role was updated"}),200)

