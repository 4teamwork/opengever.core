from datetime import date
from dateutil.relativedelta import relativedelta
from ftw.mail.mail import IMail
from opengever.document.behaviors import IBaseDocument
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.document import IDocumentSchema
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.interfaces import IDossierResolveProperties
from plone import api


class DocumentMaintenance(object):

    def get_waiting_period_deadline_date(self):
        waiting_period = api.portal.get_registry_record(
            'waiting_period_source_file_removal',
            interface=IDossierResolveProperties)

        year = date.today().year - 1 - waiting_period
        return date(year, 12, 31)

    def get_dossiers_to_erase(self):
        """Returns all dossiers with a expired waiting period, where the
        files has to be erased.
        """
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog({
            'object_provides': IDossierMarker.__identifier__,
            'dossier.review_state': 'dossier-state-resolved',
            'end': {'query': self.get_waiting_period_deadline_date(),
                    'range': 'max'}})

        return [brain.getObject() for brain in brains]

    def get_documents_to_erase_source_file(self):
        catalog = api.portal.get_tool('portal_catalog')
        paths = ['/'.join(dossier.getPhysicalPath()) for dossier in
                 self.get_dossiers_to_erase()]
        brains = catalog({'path': paths,
                          'has_archival_file': True,
                          'object_provides': IBaseDocument.__identifier__})

        return [brain.getObject() for brain in brains]

    def purge_source_files(self):
        for document in self.get_documents_to_erase_source_file():
            if not IDocumentMetadata(document).archival_file:
                raise Exception(
                    'Document {} has not archival file.'.format(document))

            if IDocumentSchema.providedBy(document):
                IDocumentSchema(document).file = None
            else:
                IMail(document).message = None
