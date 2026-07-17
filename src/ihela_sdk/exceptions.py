class iHelaError(Exception):
    """Base exception class for all iHela Client exceptions."""

    pass


class iHelaAuthenticationError(iHelaError):
    """Exception raised when client credentials or token authentication fail."""

    pass


class iHelaAPIError(iHelaError):
    """Exception raised when an API request to the iHela gateway fails.

    This exception is generic to prevent information leakage (e.g., distinguishing
    between permission issues vs. resource existence during unauthorized probing),
    while preserving the raw status code for secure developer-side debugging.
    """

    def __init__(
        self,
        message="An error occurred while communicating with the iHela gateway.",
        status_code=None,
        response_data=None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
