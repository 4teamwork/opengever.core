from zope.interface import Interface


class IBaseDocument(Interface):
    """Marker interface for objects with a document like type
    (og.document, ftw.mail.mail) etc."""
