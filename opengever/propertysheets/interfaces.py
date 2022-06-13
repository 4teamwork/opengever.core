from zope.interface import Interface


class IDuringPropertySheetFieldDeserialization(Interface):
    """Request layer to indicate that we are currently deserializing
    a property sheet field.
    """
