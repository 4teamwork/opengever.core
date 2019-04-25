from ftw.upgrade import UpgradeStep
from ftw.upgrade.progresslogger import ProgressLogger
from opengever.document.document import IDocumentSchema
from os.path import splitext
from plone import api


MS_PUBLISHER_EXTENSION = '.pub'
MS_PUBLISHER_MIMETYPE = 'application/x-mspublisher'

WMF_EXTENSION = '.wmf'
WMF_MIMETYPE = 'image/x-wmf'


class FixContenttypeForMSPublisherFiles(UpgradeStep):
    """Fix contenttype for MS Publisher and WMF files.
    """

    def __call__(self):
        self.install_upgrade_profile()

        # This upgradestep has been merged to the later one
        # (20181113161333_fix_content_type_for_open_xml_visio) to avoid
        # looping trough all document brains twice.
        return

        # catalog = api.portal.get_tool('portal_catalog')
        # brains = catalog.unrestrictedSearchResults(
        #     {'object_provides': IDocumentSchema.__identifier__})

        # for brain in ProgressLogger(
        #         'Fix contettype for MS Publisher and wmf files', brains):
        #     if brain.getContentType == 'application/octet-stream':
        #         obj = brain.getObject()
        #         if not obj.file:
        #             continue

        #         filename, ext = splitext(obj.file.filename)
        #         if ext == MS_PUBLISHER_EXTENSION:
        #             obj.file.contentType = MS_PUBLISHER_MIMETYPE
        #             obj.reindexObject()

        #         if ext == WMF_EXTENSION:
        #             obj.file.contentType = WMF_MIMETYPE
        #             obj.reindexObject()
