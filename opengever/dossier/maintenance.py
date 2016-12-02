from datetime import date
from dateutil.relativedelta import relativedelta
from ftw.mail.mail import IMail
from opengever.document.behaviors import IBaseDocument
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.document import IDocumentSchema
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.interfaces import IDossierResolveProperties
from plone import api


class SourceFileEraser(object):

    def get_waiting_period_deadline_date(self):
        waiting_period = api.portal.get_registry_record(
            'waiting_period_source_file_removal',
            interface=IDossierResolveProperties)

        return date.today() - relativedelta(years=waiting_period)

    def get_dossiers_to_erase(self):
        """Returns all dossiers with a expired waiting period, where the
        files has to be erased.
        """
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog({
            'object_provides': IDossierMarker.__identifier__,
            'end': {'query': self.get_waiting_period_deadline_date(),
                   'range': 'max'}})

        return [brain.getObject() for brain in brains]

    def erase(self):
        for dossier in self.get_dossiers_to_erase():
            for document in api.content.find(dossier, object_provides=IBaseDocument):
                self.erase_source_file(document.getObject())

    def erase_source_file(self, document):
        if not IDocumentMetadata(document).archival_file:
            return

        if IDocumentSchema.providedBy(document):
            IDocumentSchema(document).file = None

        else:
            IMail(document).message = None
