import actor_service
import movie_service
from jwt_utils import require_admin


def all_movies(_, info):
    return movie_service.get_all()

def movie_with_id(_, info, _id):
    return movie_service.get_by_id(_id)

def movies_with_ids(_, info, _ids):
    return movie_service.get_by_ids(_ids)

def movie_with_title(_, info, _title):
    return movie_service.get_by_title(_title)

def all_actors(_, info):
    return actor_service.get_all()

def actor_with_id(_, info, _id):
    return actor_service.get_by_id(_id)

def actors_by_movie(_, info, _movieid):
    return actor_service.get_by_movie(_movieid)


@require_admin
def add_movie(_, info, _movieinput):
    return movie_service.add_movie(_movieinput)

@require_admin
def update_movie(_, info, _id, _movieinput):
    return movie_service.update_movie(_id, _movieinput)

@require_admin
def del_movie(_, info, _id):
    movie = movie_service.delete_movie(_id)
    actor_service.remove_movie(_id)
    return movie

@require_admin
def add_actor(_, info, _actorinput):
    return actor_service.add_actor(_actorinput)

@require_admin
def update_actor(_, info, _id, _actorinput):
    return actor_service.update_actor(_id, _actorinput)

@require_admin
def del_actor(_, info, _id):
    return actor_service.delete_actor(_id)


def resolve_actors_in_movie(movie, info):
    return actor_service.get_by_movie(movie.get("id"))

def resolve_movies_in_actor(actor, info):
    return movie_service.get_by_ids(actor.get("films",[]))

def resolve_times_in_movie(movie, info):
    return movie_service.get_movie_times(movie.get("id"))
