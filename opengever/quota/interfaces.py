from zope.interface import Interface


class IQuotaSubject(Interface):
    """Objects providing IQuotaSubject will count to the usage
    in the quota container.
    """

    def get_size():
        """Return the current size of the context in bytes.
        """
