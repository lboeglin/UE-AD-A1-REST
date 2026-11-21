import actor_service
import movie_service
from jwt_utils import require_admin


def all_movies(_, info):
    return movie_service.get_all()

def movie_with_id(_, info, id):
    return movie_service.get_by_id(id)

def movie_with_title(_, info, title):
    return movie_service.get_by_title(title)

def all_actors(_, info):
    return actor_service.get_all()

def actor_with_id(_, info, id):
    return actor_service.get_by_id(id)

def actors_by_movie(_, info, movieid):
    return actor_service.get_by_movie(movieid)


@require_admin
def add_movie(_, info, movieinput):
    return movie_service.add_movie(movieinput)

@require_admin
def update_movie(_, info, id, movieinput):
    return movie_service.update_movie(id,movieinput)

@require_admin
def del_movie(_, info, id):
    return movie_service.delete_movie(id)

@require_admin
def add_actor(_, info, actorinput):
    return actor_service.add_actor(actorinput)

@require_admin
def update_actor(_, info, id, actorinput):
    return actor_service.update_actor(id,actorinput)

@require_admin
def del_actor(_, info, id):
    return actor_service.delete_actor(id)


def resolve_actors_in_movie(movie, info):
    return actor_service.get_by_movie(movie.get("id"))

def resolve_movies_in_actor(actor, info):
    return movie_service.get_by_ids(actor.get("films",[]))

def resolve_times_in_movie(movie, info):
    return movie_service.get_movie_times(movie.get("id"))
