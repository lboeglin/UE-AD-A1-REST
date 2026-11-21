import os
from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from flask import Flask, request, jsonify, make_response
import resolvers as r

PORT = 3201
HOST = '0.0.0.0'
app = Flask(__name__)

type_defs = load_schema_from_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'booking.graphql'))

query = QueryType()
query.set_field('bookings', r.bookings)
query.set_field('booking_with_userid', r.booking_with_userid)
query.set_field('bookings_for_movie', r.bookings_for_movie)

mutation = MutationType()
mutation.set_field('add_booking', r.add_booking)
mutation.set_field('delete_booking', r.delete_booking)

date_booking = ObjectType('DateBooking')
date_booking.set_field('movies_details', r.resolve_movies_details)

schema = make_executable_schema(type_defs, query, mutation, date_booking)

@app.route("/", methods=['GET'])
def home():
   return make_response("<h1 style='color:blue'>Welcome to the Booking service!</h1>", 200)

@app.route('/graphql', methods=['POST'])
def graphql_server():
   data = request.get_json()
   success, result = graphql_sync(schema, data, context_value={"request": request}, debug=app.debug)
   return make_response(jsonify(result), 200 if success else 400)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
