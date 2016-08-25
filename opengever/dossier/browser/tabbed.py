from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.contact import is_contact_feature_enabled
from opengever.dossier import _
from opengever.meeting import is_meeting_feature_enabled


class DossierTabbedView(TabbedView):

    overview_tab = {
        'id': 'overview',
        'title': _(u'label_overview', default=u'Overview'),
        'icon': None,
        'url': '#',
        'class': None}

    documents_tab = {
        'id': 'documents-proxy',
        'title': _(u'label_documents', default=u'Documents'),
        'icon': None,
        'url': '#',
        'class': None}

    tasks_tab = {
        'id': 'tasks',
        'title': _(u'label_tasks', default=u'Tasks'),
        'icon': None,
        'url': '#',
        'class': None}

    trash_tab = {
        'id': 'trash',
        'title': _(u'label_trash', default=u'Trash'),
        'icon': None,
        'url': '#',
        'class': None}

    journal_tab = {
        'id': 'journal',
        'title': _(u'label_journal', default=u'Journal'),
        'icon': None,
        'url': '#',
        'class': None}

    info_tab = {
        'id': 'sharing',
        'title': _(u'label_info', default=u'Info'),
        'icon': None,
        'url': '#',
        'class': None}

    @property
    def subdossiers_tab(self):
        if self.context.show_subdossier:
            return {'id': 'subdossiers',
                    'title': _(u'label_subdossiers', default=u'Subdossiers'),
                    'icon': None,
                    'url': '#',
                    'class': None}

        return None

    @property
    def proposals_tab(self):
        if is_meeting_feature_enabled():
            return {'id': 'proposals',
                    'title': _(u'label_proposals', default=u'Proposals'),
                    'icon': None,
                    'url': '#',
                    'class': None}

        return None

    @property
    def participations_tab(self):
        if is_contact_feature_enabled():
            return {
                'id': 'participations',
                'title': _(u'label_participations', default=u'Participations'),
                'icon': None,
                'url': '#',
                'class': None}

        return {
            'id': 'participants',
            'title': _(u'label_participants', default=u'Participants'),
            'icon': None,
            'url': '#',
            'class': None}

    def get_tabs(self):
        tabs = [self.overview_tab,
                self.subdossiers_tab,
                self.documents_tab,
                self.tasks_tab,
                self.proposals_tab,
                self.participations_tab,
                self.trash_tab,
                self.journal_tab,
                self.info_tab]

        # skip conditionally disabled tabs
        return [tab for tab in tabs if tab]


class TemplateDossierTabbedView(TabbedView):

    template_tab = {
        'id': 'documents-proxy',
        'title': _(u'label_documents', default=u'Documents'),
        'icon': None,
        'url': '#',
        'class': None}

    tasktemplate_folders_tab = {
        'id': 'tasktemplatefolders',
        'title': _(u'label_tasktemplate_folders',
                   default=u'Tasktemplate Folders'),
        'icon': None,
        'url': '#',
        'class': None}

    @property
    def sablon_tab(self):
        if is_meeting_feature_enabled():
            return {'id': 'sablontemplates',
                    'title': _(u'label_sablon_templates',
                               default=u'Sablon Templates'),
                    'icon': None,
                    'url': '#',
                    'class': None}

    def get_tabs(self):
        tabs = [
            self.template_tab,
            self.sablon_tab,
            self.tasktemplate_folders_tab
        ]

        # skip conditionally disabled tabs
        return [tab for tab in tabs if tab]
