from ftw.upgrade import UpgradeStep
from opengever.document.interfaces import IDossierJournalPDFMarker
from opengever.document.interfaces import IDossierTasksPDFMarker


journal_interface_name = 'opengever.document.interfaces.IDossierJournalPDFMarker'
task_interface_name = 'opengever.document.interfaces.IDossierTasksPDFMarker'


class FixTaskAndJournalPDFObjectProvides(UpgradeStep):
    """Fix task and journal pdf object provides.
    """

    def __call__(self):
        catalog = self.portal.portal_catalog
        object_provides = catalog._catalog.getIndex("object_provides")

        # first we look for journal dossiers
        title_fr = u"Journal du dossier "
        title_de = u"Dossier Journal "
        title_en = u"Journal of dossier "
        possible_titles = [title_fr, title_de, title_en]

        for title in possible_titles:
            query = {'portal_type': 'opengever.document.document', 'title': title}
            for brain in self.catalog_unrestricted_search(query):
                # If the interface is already in the index, we can skip
                if journal_interface_name in object_provides.getEntryForObject(brain.getRID(), ""):
                    continue
                obj = brain.getObject()
                # If the interface should be in the index, we need to reindex
                if IDossierJournalPDFMarker.providedBy(obj):
                    obj.reindexObject(idxs=['object_provides'])

        # Now we look for task listing pdfs
        title_fr = u"Liste des t\xe2ches du dossier "
        title_de = u"Aufgabenliste des Dossiers "
        title_en = u"Task list of dossier "
        possible_titles = [title_fr, title_de, title_en]

        for title in possible_titles:
            query = {'portal_type': 'opengever.document.document', 'title': title}
            for brain in self.catalog_unrestricted_search(query):
                # If the interface is already in the index, we can skip
                if task_interface_name in object_provides.getEntryForObject(brain.getRID(), ""):
                    continue
                obj = brain.getObject()
                # If the interface should be in the index, we need to reindex
                if IDossierTasksPDFMarker.providedBy(obj):
                    obj.reindexObject(idxs=['object_provides'])
