class ServiceKeyMissing(Exception):

    def __init__(self, url, keys, path):
        known_key_urls = repr(tuple(keys))

        super(ServiceKeyMissing, self).__init__(
            'No workspace service key found for URL {}.\n'
            'Found keys {} in the folder: {}'.format(url, known_key_urls, path))


class APIRequestException(Exception):
    """Base class for exceptions when making a request to a service app.
    This base class can be used to build custom exception classes which will then
    be raised by the api client when something bad happens in the communication
    with the service app.
    """

    message = "Request to workspaces failed."

    def __init__(self, original_exception=None):
        """
        :param original_exception: An instance of an exception. Will be logged too.
        """
        self.original_exception = original_exception
        super(APIRequestException, self).__init__(self.msg())

    def msg(self):
        msgs = [self.__class__.__name__]
        msgs.append(self.message)

        if self.original_exception:
            msgs.append("Original exception: {}.".format(self.original_exception))

            if hasattr(self.original_exception, "response") and self.original_exception.response.text:
                msgs.append("Response from service app: {}".format(self.original_exception.response.text))

        return "\n".join(msgs)
