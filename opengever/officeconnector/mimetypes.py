from plone import api


EDITABLE_TYPES = [
    # Adobe Illustrator
    'application/illustrator',
    # Adobe InDesign
    'application/x-indesign',
    # Adobe Photoshop
    'image/vnd.adobe.photoshop',
    # Apple Keynote
    'application/x-iwork-keynote-sffkey',
    # Apple Numbers
    'application/x-iwork-numbers-sffnumbers',
    # Apple Pages
    'application/x-iwork-pages-sffpages',
    # Images - MS Paint or Adobe Photoshop
    'image/bmp',
    'image/gif',
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/tiff',
    # Mindjet Mind Manager
    'application/vnd.mindjet.mindmanager',
    # MS Excel
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    # MS OneNote
    'application/onenote',
    # MS Powerpoint
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
    # MS Project
    'application/vnd.ms-project',
    'application/x-project',
    # MS Publisher
    'application/x-mspublisher',
    # MS Visio
    'application/vnd.visio',
    'application/vnd.ms-visio.drawing',
    # MS Word
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    # PDF editors - Adobe Acrobat or Nitro PDF
    'application/pdf',
    'application/postscript',
    # Richtext editors - various
    'application/rtf',
    'text/richtext',
    # Text editors - various
    'text/css',
    'text/csv',
    'text/html',
    'text/plain',
    'text/tab-separated-values',
    'text/xml',
]


def get_editable_types():
    """Return the full list of OC-editable mimetypes (lowercased).

    This function compiles the final list based on the standard set from
    EDITABLE_TYPES, plus/minus some customer-specific blacklisted / whitelisted
    types defined in registry settings.
    """
    editable_mimetypes = set(type.lower() for type in EDITABLE_TYPES)

    # Append extra MIME types from the registry
    extra_mimetypes = set(type.lower() for type in api.portal.get_registry_record(
        'opengever.officeconnector.interfaces.IOfficeConnectorSettings.officeconnector_editable_types_extra'))
    editable_mimetypes.update(extra_mimetypes)

    # Remove blacklisted-in-registry MIME types
    blacklisted_mimetypes = set(type.lower() for type in api.portal.get_registry_record(
        'opengever.officeconnector.interfaces.IOfficeConnectorSettings.officeconnector_editable_types_blacklist'))
    editable_mimetypes.difference_update(blacklisted_mimetypes)

    return editable_mimetypes
