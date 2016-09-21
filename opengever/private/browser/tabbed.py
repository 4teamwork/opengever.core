from five import grok
from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.private import _
from opengever.private.folder import IPrivateFolder
from opengever.tabbedview.browser.tabs import Dossiers


class PrivateFolderTabbedView(TabbedView):

    dossier_tab = {
        'id': 'dossiers',
        'title': _(u'label_dossiers', default=u'Dossiers'),
        'icon': None,
        'url': '#',
        'class': None}

    def get_tabs(self):
        return [self.dossier_tab]


class PrivateFolderDossiers(Dossiers):
    grok.context(IPrivateFolder)

    filterlist_available = False
