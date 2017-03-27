from ftw.upgrade import UpgradeStep
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.dossier.interfaces import IDossierResolveProperties
from plone import api


class FixContentypesEncodingForArchivalFiles(UpgradeStep):
    """Fix contentypes encoding for archival files.
    """

    def __call__(self):
        # Skip contentype fixing for installation where the conversion
        # has not be enabled yet.
        if not self.is_conversion_enabled():
            return

        for obj in self.objects(
                {'object_provides': IDocumentMetadata.__identifier__},
                'Fix contenttype encoding for archival files'):

            self.fix_contenttype_encoding(obj)

    def is_conversion_enabled(self):
        try:
            return api.portal.get_registry_record(
                'archival_file_conversion_enabled',
                interface=IDossierResolveProperties)
        except KeyError:
            return False

    def fix_contenttype_encoding(self, document):
        if not IDocumentMetadata(document).archival_file:
            return

        content_type = document.archival_file.contentType
        if isinstance(content_type, unicode):
            document.archival_file.contentType = content_type.encode('utf-8')
