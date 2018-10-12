class OneoffixxConfigurationException(Exception):
    """Provide error handling for Oneoffixx configuration errors."""


class OneoffixxBackendException(Exception):
    """Provide error handling for Oneoffixx backend errors."""

    def __init__(self, message, response, error=None):
        """Capture the response and optionally the requests error as well."""
        super(OneoffixxBackendException, self).__init__(message)
        self.response = response
        self.error = error
