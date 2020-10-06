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
    # CADwork
    'application/x-cadwork-2d-lines',
    'application/x-cadwork-2d',
    'application/x-cadwork-2dm',
    'application/x-cadwork-2dr',
    'application/x-cadwork-3d',
    'application/x-cadwork-catalog-2d',
    'application/x-cadwork-catalog-3d',
    'application/x-cadwork-lexo2d',
    'application/x-cadwork-lexocad',
    'application/x-cadwork-lexoview',
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
    'application/vnd.ms-excel.addin.macroEnabled.12',
    'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
    'application/vnd.ms-excel.sheet.macroEnabled.12',
    'application/vnd.ms-excel.template.macroEnabled.12',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
    # MS OneNote
    'application/onenote',
    # MS Powerpoint
    'application/vnd.ms-powerpoint.addin.macroEnabled.12',
    'application/vnd.ms-powerpoint.presentation.macroEnabled.12',
    'application/vnd.ms-powerpoint.slideshow.macroEnabled.12',
    'application/vnd.ms-powerpoint.template.macroEnabled.12',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
    'application/vnd.openxmlformats-officedocument.presentationml.template',
    # MS Project
    'application/vnd.ms-project',
    'application/x-project',
    # MS Publisher
    'application/x-mspublisher',
    # MS Visio
    'application/vnd.ms-visio.drawing.macroEnabled.12',
    'application/vnd.ms-visio.drawing',
    'application/vnd.ms-visio.stencil.macroEnabled.12',
    'application/vnd.ms-visio.stencil',
    'application/vnd.ms-visio.template.macroEnabled.12',
    'application/vnd.ms-visio.template',
    'application/vnd.visio',
    # MS Word
    'application/msword',
    'application/vnd.ms-word.document.macroEnabled.12',
    'application/vnd.ms-word.template.macroEnabled.12',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
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
