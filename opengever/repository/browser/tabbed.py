from opengever.repository import _
from opengever.repository.interfaces import IRepositoryFolderRecords
from opengever.tabbedview import GeverTabbedView
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class RepositoryRootTabbedView(GeverTabbedView):
    """Define the tabs available on a Repository Root."""

    overview_tab = {
        'id': 'overview',
        'title': _(u'label_overview', default=u'Overview'),
        }

    dossiers_tab = {
        'id': 'dossiers',
        'title': _(u'label_dossiers', default=u'Dossiers'),
        }

    info_tab = {
        'id': 'sharing',
        'title': _(u'label_info', default=u'Info'),
        }

    @property
    def dispositions_tab(self):
        if api.user.has_permission('opengever.disposition: Add disposition', obj=self.context):
            return {
                'id': 'dispositions',
                'title': _(u'label_dispositions', default=u'Dispositions'),
                }
        return None

    @property
    def journal_tab(self):
        if api.user.has_permission('Sharing page: Delegate roles', obj=self.context):
            return {
                'id': 'journal',
                'title': _(u'label_journal', default=u'Journal'),
                }
        return None

    @property
    def blocked_local_roles_tab(self):
        if api.user.has_permission('opengever.sharing: List Protected Objects', obj=self.context):
            return {
                'id': 'blocked-local-roles',
                'title': _(u'label_blocked_local_roles', default=u'Protected Objects'),
                }
        return None

    def _get_tabs(self):
        return filter(None, [
            self.overview_tab,
            self.dossiers_tab,
            self.dispositions_tab,
            self.info_tab,
            self.blocked_local_roles_tab,
            self.journal_tab,
        ])


class RepositoryFolderTabbedView(GeverTabbedView):
    """Define the tabs available on a Repository Root."""

    dossiers_tab = {
        'id': 'dossiers',
        'title': _(u'label_dossiers', default=u'Dossiers'),
        }

    info_tab = {
        'id': 'sharing',
        'title': _(u'label_info', default=u'Info'),
        }

    @property
    def blocked_local_roles_tab(self):
        if api.user.has_permission('opengever.sharing: List Protected Objects', obj=self.context):
            return {
                'id': 'blocked-local-roles',
                'title': _(u'label_blocked_local_roles', default=u'Protected Objects'),
                }
        return None

    @property
    def documents_tab(self):
        settings = getUtility(IRegistry).forInterface(IRepositoryFolderRecords)
        if getattr(settings, 'show_documents_tab', False):
            return {
                'id': 'documents-proxy',
                'title': _(u'label_documents', default=u'Documents'),
                }
        return None

    @property
    def tasks_tab(self):
        settings = getUtility(IRegistry).forInterface(IRepositoryFolderRecords)
        if getattr(settings, 'show_tasks_tab', False):
            return {
                'id': 'tasks',
                'title': _(u'label_tasks', default=u'Tasks'),
                }
        return None

    def _get_tabs(self):
        return filter(None, [
            self.dossiers_tab,
            self.documents_tab,
            self.tasks_tab,
            self.info_tab,
            self.blocked_local_roles_tab,
        ])
