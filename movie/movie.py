from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from flask import Flask, request, jsonify, make_response

import resolvers as r

app = Flask(__name__)

PORT = 3200
HOST = '0.0.0.0'

type_defs = load_schema_from_path('movie.graphql')
query = QueryType()
mutation = MutationType()
movie = ObjectType('Movie')
actor = ObjectType('Actor')

query.set_field('movie_with_id', r.movie_with_id)
query.set_field('all_movies', r.all_movies)
query.set_field('movie_with_title', r.movie_with_title)

query.set_field('all_actors', r.all_actors)
query.set_field('actor_with_id', r.actor_with_id)
query.set_field('actors_by_movie', r.actors_by_movie)

mutation.set_field('add_movie',r.add_movie)
mutation.set_field('update_movie',r.update_movie)
mutation.set_field('del_movie',r.del_movie)

mutation.set_field('add_actor',r.add_actor)
mutation.set_field('update_actor',r.update_actor)
mutation.set_field('del_actor',r.del_actor)

movie.set_field('actors', r.resolve_actors_in_movie)
movie.set_field('times', r.resolve_times_in_movie)
actor.set_field('films', r.resolve_movies_in_actor)

schema = make_executable_schema(type_defs, movie,actor,query,mutation)

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

# graphql entry points
@app.route('/graphql', methods=['POST'])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request, # Pour gérer les permissions on doit ajouter la requete
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)
