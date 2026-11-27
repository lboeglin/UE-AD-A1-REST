from errors import NotFoundError, ValidationError, ServiceUnavailableError, UpstreamError
from jwt_utils import AuthenticationError

CODES = [
    (NotFoundError, "NOT_FOUND"),
    (ValidationError, "BAD_USER_INPUT"),
    (AuthenticationError, "UNAUTHENTICATED"),
    (PermissionError, "FORBIDDEN"),
    (ServiceUnavailableError, "SERVICE_UNAVAILABLE"),
    (UpstreamError, "UPSTREAM_ERROR"),
]

def error_code(original):
    return next((code for cls, code in CODES if isinstance(original, cls)), None)

def format_error(error, debug=False):
    formatted = dict(error.formatted)
    extensions = dict(formatted.get("extensions") or {})
    original = error.original_error
    if original is None:
        extensions.setdefault("code", "GRAPHQL_VALIDATION_FAILED")
    elif error_code(original):
        extensions["code"] = error_code(original)
    else:
        formatted["message"] = "internal server error"
        extensions["code"] = "INTERNAL_SERVER_ERROR"
    formatted["extensions"] = extensions
    return formatted
