from opengever.dossier.browser.tabbed import DossierTabbedView
from opengever.private import _
from opengever.tabbedview import GeverTabbedView
from opengever.tabbedview.browser.tabs import Documents
from opengever.tabbedview.browser.tabs import Dossiers


class PrivateFolderTabbedView(GeverTabbedView):

    dossier_tab = {
        'id': 'dossiers',
        'title': _(u'label_dossiers', default=u'Dossiers')
    }

    def _get_tabs(self):
        return [self.dossier_tab]


class PrivateFolderDossiers(Dossiers):

    enabled_actions = ['pdf_dossierlisting', 'export_dossiers']


class PrivateDossierTabbedView(DossierTabbedView):
    """Overwrite the DossierTabbedview to hide the task, proposal,
    participation and info tab.
    """

    def _get_tabs(self):
        return [self.overview_tab,
                self.subdossiers_tab,
                self.documents_tab,
                self.trash_tab,
                self.journal_tab]


class PrivateDossierDocuments(Documents):

    @property
    def columns(self):
        columns = super(PrivateDossierDocuments, self).columns
        cols_by_name = {col['column']: col for col in columns}
        cols_by_name['public_trial']['hidden'] = True
        cols_by_name['receipt_date']['hidden'] = True
        cols_by_name['delivery_date']['hidden'] = True
        return columns
