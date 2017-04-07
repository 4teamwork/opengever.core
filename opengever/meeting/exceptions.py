class NoSubmittedDocument(Exception):
    """A document could not be updates remotely since it is not a submitted
    document.
    """


class ProtocolAlreadyGenerated(Exception):
    """The protocol could not be generated since another protocl is already
    present.
    """


class WordMeetingImplementationDisabledError(Exception):
    """The word meeting implementation feature is not enabled but a method
    was called which requires this feature.
    """
