from ftw.keywordwidget import _ as KWMF
from opengever.base.handlebars import get_handlebars_template
from opengever.workspace import _
from opengever.workspace.participation import PARTICIPATION_ROLES
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
import json
import os


class ParticipantsView(BrowserView):

    template = ViewPageTemplateFile('templates/participants-view.pt')

    @property
    def table_template(self):
        return get_handlebars_template(os.path.join(os.path.dirname(__file__),
                                                    'templates',
                                                    'table.html'))

    def __call__(self):
        return self.template()

    def translations(self):

        return json.dumps({
            'label_placeholder': translate(_('Select a user ...'), context=self.request),
            'label_no_result': translate(KWMF('No result found'), context=self.request),
            'label_searching': translate(KWMF(u'Searching...'), context=self.request),
            'label_loading_more': translate(KWMF('Load more results...'), context=self.request),
            'label_tooshort_prefix': translate(KWMF('Please enter '), context=self.request),
            'label_tooshort_postfix': translate(KWMF(' or more characters'), context=self.request),
            'workspaceguest': PARTICIPATION_ROLES.get('WorkspaceGuest').translated_title(self.request),
            'workspacemember': PARTICIPATION_ROLES.get('WorkspaceMember').translated_title(self.request),
            'workspaceadmin': PARTICIPATION_ROLES.get('WorkspaceAdmin').translated_title(self.request),
            'workspaceowner': PARTICIPATION_ROLES.get('WorkspaceOwner').translated_title(self.request),
            'user': translate(_('User'), context=self.request),
            'type': translate(_('Type'), context=self.request),
            'role': translate(_('Rolle'), context=self.request),
            'action': translate(_('Action'), context=self.request),
            'delete_action': translate(_('Delete'), context=self.request),
            'type_invitation': translate(_('Invitation'), context=self.request),
            'type_user': translate(_('User'), context=self.request),
            'invite': translate(_('Invite'), context=self.request),
            'invited_by': translate(_('Invited by:'), context=self.request),
            'message_updated': translate(_('Role updated'), context=self.request),
            'message_invited': translate(_('Participant invited'), context=self.request),
            'message_deleted': translate(_('Participant deleted'), context=self.request),
        })
