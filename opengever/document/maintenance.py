from datetime import date
from ftw.mail.mail import IMail
from opengever.document.behaviors import IBaseDocument
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.document import IDocumentSchema
from opengever.document.events import SourceFilePurged
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.interfaces import IDossierResolveProperties
from opengever.dossier.interfaces import ISourceFileHasBeenPurged
from opengever.dossier.events import SourceFilesPurged
from plone import api
from zope.event import notify
from zope.interface import alsoProvides


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
            'review_state': 'dossier-state-resolved',
            'end': {'query': self.get_waiting_period_deadline_date(),
                    'range': 'max'}})

        return [brain.getObject() for brain in brains
                if not ISourceFileHasBeenPurged.providedBy(brain.getObject())]

    def get_documents_to_erase_source_file(self, dossiers):
        catalog = api.portal.get_tool('portal_catalog')
        paths = ['/'.join(dossier.getPhysicalPath()) for dossier in dossiers]
        brains = catalog({'path': paths,
                          'has_archival_file': True,
                          'object_provides': IBaseDocument.__identifier__})

        return [brain.getObject() for brain in brains]

    def purge_source_files(self):
        dossiers = self.get_dossiers_to_erase()
        for document in self.get_documents_to_erase_source_file(dossiers):
            if not IDocumentMetadata(document).archival_file:
                raise Exception(
                    'Document {} has not archival file.'.format(document))

            if IDocumentSchema.providedBy(document):
                IDocumentSchema(document).file = None
            else:
                IMail(document).message = None

            notify(SourceFilePurged(document))

        for dossier in dossiers:
            self.mark_dossier(dossier)
            notify(SourceFilesPurged(dossier))

    def mark_dossier(self, dossier):
        """Mark dossier with ISourceFileHasBeenPurged marker interface.
        To make sure the dossiers are excluded from next source file purgements.
        """
        alsoProvides(dossier, ISourceFileHasBeenPurged)
