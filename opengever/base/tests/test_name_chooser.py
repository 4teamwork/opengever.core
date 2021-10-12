from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.content.interfaces import INameFromTitle
from zope.dottedname.resolve import resolve

# Please update the content creation in the test below, when a new type needs
# to be added here!
EXPECTED_TYPES_WITH_NAME_FROM_TITLE = [
    'ftw.mail.mail',
    'opengever.contact.contact',
    'opengever.contact.contactfolder',
    'opengever.disposition.disposition',
    'opengever.document.document',
    'opengever.dossier.businesscasedossier',
    'opengever.dossier.dossiertemplate',
    'opengever.dossier.templatefolder',
    'opengever.inbox.container',
    'opengever.inbox.forwarding',
    'opengever.inbox.inbox',
    'opengever.meeting.committee',
    'opengever.meeting.committeecontainer',
    'opengever.meeting.meetingdossier',
    'opengever.meeting.meetingtemplate',
    'opengever.meeting.paragraphtemplate',
    'opengever.meeting.period',
    'opengever.meeting.proposal',
    'opengever.meeting.proposaltemplate',
    'opengever.meeting.sablontemplate',
    'opengever.private.dossier',
    'opengever.private.root',
    'opengever.task.task',
    'opengever.tasktemplates.tasktemplatefolder',
    'opengever.workspace.folder',
    'opengever.workspace.meeting',
    'opengever.workspace.meetingagendaitem',
    'opengever.workspace.todo',
    'opengever.workspace.todolist',
    'opengever.workspace.workspace',
]


type_to_obj = {
    'ftw.mail.mail': 'mail_eml',
    'opengever.contact.contact': 'hanspeter_duerr',
    'opengever.contact.contactfolder': 'contactfolder',
    'opengever.disposition.disposition': 'disposition',
    'opengever.document.document': 'document',
    'opengever.dossier.businesscasedossier': 'dossier',
    'opengever.dossier.dossiertemplate': 'dossiertemplate',
    'opengever.dossier.templatefolder': 'subtemplates',
    'opengever.inbox.container': 'inbox_container',
    'opengever.inbox.forwarding': 'inbox_forwarding',
    'opengever.inbox.inbox': 'inbox',
    'opengever.meeting.committee': 'committee',
    'opengever.meeting.committeecontainer': 'committee_container',
    'opengever.meeting.meetingdossier': 'meeting_dossier',
    'opengever.meeting.meetingtemplate': 'meeting_template',
    'opengever.meeting.paragraphtemplate': 'paragraph_template',
    'opengever.meeting.period': 'period',
    'opengever.meeting.proposal': 'proposal',
    'opengever.meeting.proposaltemplate': 'proposal_template',
    'opengever.meeting.sablontemplate': 'sablon_template',
    'opengever.private.dossier': 'private_dossier',
    'opengever.private.root': 'private_root',
    'opengever.task.task': 'task',
    'opengever.tasktemplates.tasktemplatefolder': 'tasktemplatefolder',
    'opengever.workspace.folder': 'workspace_folder',
    'opengever.workspace.meeting': 'workspace_meeting',
    'opengever.workspace.meetingagendaitem': 'workspace_meeting_agenda_item',
    'opengever.workspace.todo': 'todo',
    'opengever.workspace.todolist': 'todolist_general',
    'opengever.workspace.workspace': 'workspace',
}

TYPES_WITH_UNIMPLEMENTED_NAME_FROM_TITLE = [
    'opengever.contact.contactfolder',
    'opengever.dossier.templatefolder',
    'opengever.inbox.container',
    'opengever.inbox.inbox',
    'opengever.meeting.committeecontainer',
]


def has_name_from_title_behavior(fti):
    for behavior_name in getattr(fti, 'behaviors', []):
        behavior = resolve(behavior_name)
        if issubclass(behavior, INameFromTitle):
            return True
    return False


class TestNameFromTitleBehavior(IntegrationTestCase):

    maxDiff = None

    def test_portal_types_with_name_from_title_behavior(self):
        types_with_name_from_title = filter(
            has_name_from_title_behavior, api.portal.get_tool('portal_types').values())

        self.assertItemsEqual(
            EXPECTED_TYPES_WITH_NAME_FROM_TITLE,
            [each.id for each in types_with_name_from_title],
            'There is a new type with the name chooser behavior.')

    def test_name_from_title_behavior_is_implemented_for_all_expected_types(self):
        self.login(self.manager)
        for portal_type in EXPECTED_TYPES_WITH_NAME_FROM_TITLE:
            if portal_type in TYPES_WITH_UNIMPLEMENTED_NAME_FROM_TITLE:
                continue
            obj = getattr(self, type_to_obj[portal_type])
            self.assertEqual(portal_type, obj.portal_type)
            self.assertTrue(
                INameFromTitle(obj).title,
                'NameFromTitle is not implemented for {}'.format(portal_type))

        for portal_type in TYPES_WITH_UNIMPLEMENTED_NAME_FROM_TITLE:
            obj = getattr(self, type_to_obj[portal_type])
            self.assertEqual(portal_type, obj.portal_type)
            self.assertFalse(
                INameFromTitle(obj).title,
                'NameFromTitle is unexpectedly implemented for {}'.format(portal_type))
