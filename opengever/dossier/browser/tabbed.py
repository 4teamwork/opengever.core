from opengever.contact import is_contact_feature_enabled
from opengever.dossier import _
from opengever.dossier.dossiertemplate import is_dossier_template_feature_enabled
from opengever.meeting import is_meeting_feature_enabled
from opengever.meeting import is_word_meeting_implementation_enabled
from opengever.tabbedview import GeverTabbedView


class DossierTabbedView(GeverTabbedView):

    overview_tab = {
        'id': 'overview',
        'title': _(u'label_overview', default=u'Overview'),
        }

    documents_tab = {
        'id': 'documents-proxy',
        'title': _(u'label_documents', default=u'Documents'),
        }

    tasks_tab = {
        'id': 'tasks',
        'title': _(u'label_tasks', default=u'Tasks'),
        }

    trash_tab = {
        'id': 'trash',
        'title': _(u'label_trash', default=u'Trash'),
        }

    journal_tab = {
        'id': 'journal',
        'title': _(u'label_journal', default=u'Journal'),
        }

    info_tab = {
        'id': 'sharing',
        'title': _(u'label_info', default=u'Info'),
        }

    def is_subdossier_visible(self):
        """Depending on the `respect_max_depth' property we check if
        subdossiers are addable or not.
        """

        if self.context.is_subdossier_addable():
            return True

        return self.context.has_subdossiers()

    @property
    def subdossiers_tab(self):
        if self.is_subdossier_visible():
            return {
                'id': 'subdossiers',
                'title': _(u'label_subdossiers', default=u'Subdossiers'),
                }

        return None

    @property
    def proposals_tab(self):
        if is_meeting_feature_enabled():
            return {'id': 'proposals',
                    'title': _(u'label_proposals', default=u'Proposals')}
        else:
            return None

    @property
    def participations_tab(self):
        if is_contact_feature_enabled():
            return {
                'id': 'participations',
                'title': _(u'label_participations', default=u'Participations')}
        else:
            return {
                'id': 'participants',
                'title': _(u'label_participants', default=u'Participants')}

    def _get_tabs(self):
        return filter(None, [
            self.overview_tab,
            self.subdossiers_tab,
            self.documents_tab,
            self.tasks_tab,
            self.proposals_tab,
            self.participations_tab,
            self.trash_tab,
            self.journal_tab,
            self.info_tab,
        ])


class TemplateFolderTabbedView(GeverTabbedView):

    template_tab = {
        'id': 'documents-proxy',
        'title': _(u'label_documents', default=u'Documents'),
        }

    tasktemplate_folders_tab = {
        'id': 'tasktemplatefolders',
        'title': _(u'label_tasktemplate_folders',
                   default=u'Tasktemplate Folders'),
        }

    @property
    def sablon_tab(self):
        if is_meeting_feature_enabled():
            return {'id': 'sablontemplates-proxy',
                    'title': _(u'label_sablon_templates',
                               default=u'Sablon Templates')}
        else:
            return None

    @property
    def proposal_templates_tab(self):
        if is_word_meeting_implementation_enabled():
            return {'id': 'proposaltemplates-proxy',
                    'title': _(u'label_proposal_templates',
                               default=u'Proposal Templates')}
        else:
            return None

    @property
    def dossiertemplate_tab(self):
        if is_dossier_template_feature_enabled():
            return {'id': 'dossiertemplates',
                    'title': _(u'label_dossier_templates',
                               default=u'Dossier templates')}
        else:
            return None

    def _get_tabs(self):
        return filter(None, [
            self.template_tab,
            self.dossiertemplate_tab,
            self.sablon_tab,
            self.proposal_templates_tab,
            self.tasktemplate_folders_tab
        ])


class DossierTemplateTabbedView(DossierTabbedView):

    def _get_tabs(self):
        return filter(None, [
            self.overview_tab,
            self.subdossiers_tab,
            self.documents_tab,
        ])
