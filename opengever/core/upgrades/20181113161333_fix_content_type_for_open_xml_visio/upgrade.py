from ftw.upgrade import UpgradeStep
from ftw.upgrade.progresslogger import ProgressLogger
from opengever.document.document import IDocumentSchema
from os.path import splitext
from plone import api


EXTENSION_TO_MIMETYPE = {
    # Office Open XML Visio Drawing (macro-free)
    '.vsdx': 'application/vnd.ms-visio.drawing',

    # Office Open XML Visio Template (macro-free)
    '.vstx': 'application/vnd.ms-visio.template',

    # Office Open XML Visio Stencil (macro-free)
    '.vssx': 'application/vnd.ms-visio.stencil',

    # Office Open XML Visio Drawing (macro-enabled)
    '.vsdm': 'application/vnd.ms-visio.drawing.macroEnabled.12',

    # Office Open XML Visio Template (macro-enabled)
    '.vstm': 'application/vnd.ms-visio.template.macroEnabled.12',

    # Office Open XML Visio Stencil (macro-enabled)
    '.vssm': 'application/vnd.ms-visio.stencil.macroEnabled.12',

    # The following two extensions has been merged from the former upgradestep
    # 20180911140637_fix_contenttype_for_ms_publisher_files

    # MS Publisher
    '.pub': 'application/x-mspublisher',

    # Windows Metafile (WMF)
    '.wmf': 'image/x-wmf',
}


class FixContentTypeForOpenXMLVisio(UpgradeStep):
    """Fix content type for Open XML Visio.
    """

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()

        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            {'object_provides': IDocumentSchema.__identifier__})

        for brain in ProgressLogger(
                'Fix content type for Open XML Visio.', brains):
            if brain.getContentType == 'application/octet-stream':
                obj = brain.getObject()
                if not obj.file:
                    continue

                filename, ext = splitext(obj.file.filename)
                mime_type = EXTENSION_TO_MIMETYPE.get(ext)
                if not mime_type:
                    continue

                obj.file.contentType = mime_type
                obj.reindexObject()
