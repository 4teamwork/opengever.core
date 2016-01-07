from plone.namedfile.interfaces import INamedFile
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.ExternalEditor.ExternalEditor import registerCallback


def register_ee_filename_callback():
    """Register a callback function for ZEM generation in
    Products.ExternalEditor to include a document's filename in the metadata.
    """
    registerCallback(add_filename_to_metadata)


def add_filename_to_metadata(ob, metadata, request, response):
    try:
        field = IPrimaryFieldInfo(ob).field
    except TypeError:
        return

    value = field.get(ob)
    if INamedFile.providedBy(value):
        filename = getattr(value, 'filename', None)
        if filename is not None:
            metadata.insert(0, 'filename:%s' % filename.encode('utf-8'))
