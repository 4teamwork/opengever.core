from zope.interface import Interface


HARD_LIMIT_EXCEEDED = 'hard limit is exceeded'
SOFT_LIMIT_EXCEEDED = 'soft limit is exceeded'


class IObjectSize(Interface):
    """Adapter for getting size of an object.
    """

    def __init__(context):
        """Adapts a context.
        """

    def get_size():
        """Return the current size of the context in bytes.
        """


class IQuotaSizeSettings(Interface):
    """The quota settings adapter provides limits for the adapter quota
    container.
    """

    def __init__(context):
        """Adapts a IContainerWithSizeQuota context.
        """

    def get_soft_limit():
        """Return the soft limit in bytes (int), where 0 means unlimited.
        """

    def get_hard_limit():
        """Return the hard  limit in bytes (int), where 0 means unlimited.
        """
