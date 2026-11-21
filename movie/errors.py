"""
File used by movie_service, actor_service and jwt_utils to share the same exceptions.
"""

class NotFoundError(Exception):
    pass

class ValidationError(Exception):
    pass

class UnauthorizedError(Exception):
    """The Bearer token is missing."""
    pass

class ForbiddenError(Exception):
    """The user does not have required right"""
    pass

class ServiceUnavailableError(Exception):
    """Another service could not be reached."""
    pass

class UpstreamError(Exception):
    """Another service answered with an unexpected error."""
    pass