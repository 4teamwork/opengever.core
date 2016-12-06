from datetime import date
from dateutil.relativedelta import relativedelta
from ftw.mail.mail import IMail
from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from opengever.document.behaviors import IBaseDocument
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.document import IDocumentSchema
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.events import SourceFileErased
from opengever.dossier.interfaces import IDossierResolveProperties
from opengever.dossier.interfaces import ISourceFileHasBeenErased
from plone import api
from zope.event import notify
from zope.interface import alsoProvides
import logging
import transaction


logger = logging.getLogger('opengever.dossier')
logger.setLevel(logging.INFO)


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
        brains = catalog.unrestrictedSearchResults(
            {'object_provides': IDossierMarker.__identifier__,
             'review_state': 'dossier-state-resolved',
             'end': {'query': self.get_waiting_period_deadline_date(),
                     'range': 'max'}})

        return [brain.getObject() for brain in brains]

    def erase(self):
        logger.info('Source file erasement started.')
        dossiers = self.get_dossiers_to_erase()

        for dossier in dossiers:
            if ISourceFileHasBeenErased.providedBy(dossier):
                logger.info(
                    '{} skipped, erasment already done.'.format(dossier))
                continue

            catalog = api.portal.get_tool('portal_catalog')
            documents = catalog.unrestrictedSearchResults(
                {'object_provides': IBaseDocument.__identifier__,
                 'path': '/'.join(dossier.getPhysicalPath())})

            for document in documents:
                self.erase_source_file(document.getObject())

            alsoProvides(dossier, ISourceFileHasBeenErased)
            notify(SourceFileErased(dossier))

        logger.info('Source files of {} dossiers erased'.format(len(dossiers)))

    def erase_source_file(self, document):
        if not IDocumentMetadata(document).archival_file:
            return

        if IDocumentSchema.providedBy(document):
            IDocumentSchema(document).file = None

        else:
            IMail(document).message = None

        notify(SourceFileErased(document))


def source_file_eraser_zopectl_handler(app, args):
    # Set Zope's default StreamHandler's level to INFO (default is WARNING)
    # to make sure SourceFileEraser()'s output gets logged on console
    stream_handler = logger.root.handlers[0]
    stream_handler.setLevel(logging.INFO)

    setup_plone(get_first_plone_site(app))
    SourceFileEraser().erase()
    transaction.commit()
