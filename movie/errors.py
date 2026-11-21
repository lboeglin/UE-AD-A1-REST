"""
File used by movie_service and actor_service to share the same exceptions.
"""

class NotFoundError(Exception):
    pass

class ValidationError(Exception):
    pass

class ServiceUnavailableError(Exception):
    """Another service could not be reached."""
    pass

class UpstreamError(Exception):
    """Another service answered with an unexpected error."""
    pass