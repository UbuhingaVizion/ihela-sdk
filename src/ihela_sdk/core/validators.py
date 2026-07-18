from typing import Any

from .exceptions import iHelaAPIError


def validate_response(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the iHela response envelope.

    iHela response format:
      {"success": true/false, "response_code": "00", "response_message": "...", ...}

    If ``response_code != "00"``, raises a generic ``iHelaAPIError`` with the
    ``response_code`` attached for programmatic handling.

    The message is always the same generic string — never the server's
    ``response_message`` — to prevent information leakage.
    """
    response_code = data.get("response_code")
    status_code = data.get("response_status")

    if isinstance(status_code, int) and status_code >= 400:
        raise iHelaAPIError(
            status_code=status_code,
            response_code=response_code,
            response_data=data,
        )

    if response_code is not None and response_code != "00":
        raise iHelaAPIError(
            status_code=status_code,
            response_code=response_code,
            response_data=data,
        )

    return data
