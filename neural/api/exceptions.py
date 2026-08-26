"""Custom exception handling for API v1."""

from rest_framework.views import exception_handler


def flatten_detail_exception_handler(exc, context):
    """Return ``detail`` as a string instead of a list.

    ``serializers.ValidationError({"detail": "..."})`` makes DRF wrap the
    message in a list, so the API answers ``{"detail": ["Credenciales
    inválidas"]}``. The mobile app feeds that value straight into
    ``Alert.alert``, and iOS crashes when it gets an array where it expects a
    string.

    Field errors keep their list shape -- the app relies on it to show errors
    next to each input.
    """
    response = exception_handler(exc, context)
    if response is None:
        return response

    data = response.data
    if isinstance(data, dict):
        detail = data.get("detail")
        if isinstance(detail, (list, tuple)) and len(detail) == 1:
            data["detail"] = str(detail[0])

    return response
