from ftw.upgrade import UpgradeStep
from plone import api
from opengever.base.sentry import log_msg_to_sentry
from opengever.document.interfaces import IDossierJournalPDFMarker
from opengever.document.interfaces import IDossierTasksPDFMarker
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
import logging

try:
    from opengever.dossier.interfaces import IDossierJournalPdfMarker
    from opengever.dossier.interfaces import IDossierTasksPdfMarker
except ImportError:
    IDossierJournalPdfMarker = None
    IDossierTasksPdfMarker = None


LOG = logging.getLogger('ftw.upgrade')


class AddAutomaticallyGeneratedDocumentInterface(UpgradeStep):
    """Add automatically generated document interface.
    """

    interface_mapping = {IDossierJournalPdfMarker: IDossierJournalPDFMarker,
                         IDossierTasksPdfMarker: IDossierTasksPDFMarker}

    def __call__(self):
        if None in self.interface_mapping:
            brains = api.content.find(object_provides=['opengever.dossier.interfaces.IDossierJournalPdfMarker',
                                                       'opengever.dossier.interfaces.IDossierTasksPdfMarker'])

            if len(brains) > 0:
                error = "Trying to execute upgrade step AddAutomaticallyGeneratedDocumentInterface\n"
                error += "after 'opengever.dossier.interfaces.IDossierJournalPdfMarker' and\n"
                error += "'opengever.dossier.interfaces.IDossierTasksPdfMarker' have already\n"
                error += "been removed from code. There are {} objects\n".format(len(brains))
                error += "left displaying one of these interfaces."

                log_msg_to_sentry(error)
                LOG.warning("Sent message to sentry:")
                LOG.warning(error)
            return

        for old_interface, new_interface in self.interface_mapping.items():
            query = {'object_provides': [old_interface.__identifier__]}
            message = 'Map {} to {}'.format(old_interface.__identifier__,
                                            new_interface.__identifier__)
            for obj in self.objects(query, message):
                alsoProvides(obj, new_interface)
                noLongerProvides(obj, old_interface)
                obj.reindexObject(idxs=['object_provides'])
