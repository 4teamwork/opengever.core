from ftw.solr.interfaces import ISolrConnectionManager
from ftw.solr.interfaces import ISolrIndexHandler
from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.propertysheets.assignment import get_dossier_assignment_slots
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from zope.component import getMultiAdapter
from zope.component import getUtility


class ReindexCustompropertiesForDossier(UpgradeStep):
    """Reindex customproperties for dossier.
    """

    deferrable = True

    def __call__(self):
        # We only need to reindex, if there are propertysheeets registered for
        # dossiers
        if not self.has_dossier_propertysheet_registered():
            return

        manager = getUtility(ISolrConnectionManager)
        query = {'object_provides': IDossierMarker.__identifier__}
        for obj in self.objects(query, 'Reindex solr customproperties'):
            handler = getMultiAdapter((obj, manager), ISolrIndexHandler)
            handler.add([])

        manager.connection.commit(soft_commit=False, after_commit=False)

    def has_dossier_propertysheet_registered(self):
        storage = PropertySheetSchemaStorage()
        slots = get_dossier_assignment_slots()

        for slot in slots:
            if storage.query(slot):
                return True

        return False
