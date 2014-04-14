from zope.interface import Interface


class IMailInAddressMarker(Interface):
    """DEPRECATED behavior marker interface.

    We only keep this to avoid errors in regard to persistent interface names.
    """


class ISendableDocsContainer(Interface):
    """Marker interface which states that the `send_documents` action is
    callable on this container type.
    """
