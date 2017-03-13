from zExceptions import Forbidden


class ForbiddenByQuota(Forbidden):
    """Forbiddden because the quota hard limit is reached.
    """

    def __init__(self, message, container):
        self.container = container
        super(ForbiddenByQuota, self).__init__(message)
