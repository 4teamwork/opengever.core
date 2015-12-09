from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.model import Meeting
from opengever.meeting.model.agendaitem import AgendaItem
from opengever.meeting.wrapper import MeetingWrapper
from opengever.testing import FunctionalTestCase
from plone.protect import createToken
from plone.protect import createToken
from z3c.relationfield.relation import RelationValue
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import json


class TestAgendaItem(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestAgendaItem, self).setUp()
        self.admin_unit.public_url = 'http://nohost/plone'

        self.repository_root, self.repository_folder = create(
            Builder('repository_tree'))
        self.dossier = create(
            Builder('dossier').within(self.repository_folder))
        self.meeting_dossier = create(
            Builder('meeting_dossier').within(self.repository_folder))
        self.container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(self.container))
        self.meeting = create(Builder('meeting')
                              .having(committee=self.committee.load_model())
                              .link_with(self.meeting_dossier))

        self.meeting_wrapper = MeetingWrapper.wrap(self.committee, self.meeting)

    def setup_proposal(self, has_document=False):
        builder = (Builder('proposal')
                   .within(self.dossier)
                   .having(committee=self.committee.load_model())
                   .as_submitted())

        if has_document:
            document = create(Builder('document').within(self.dossier))
            builder = builder.relate_to(document)

        return create(builder)

    def schedule_proposal(self, proposal, browser):
        view = 'unscheduled_proposals/{}/schedule'.format(
            proposal.load_model().proposal_id)

        browser.login().open(self.meeting_wrapper, view=view)

        return AgendaItem.query.first()

    def setup_excerpt_template(self):
        templates = create(Builder('templatedossier'))
        sablon_template = create(
            Builder('sablontemplate')
            .within(templates)
            .with_asset_file('sablon_template.docx'))

        self.container.excerpt_template = RelationValue(
            getUtility(IIntIds).getId(sablon_template))


class TestAgendaItemList(TestAgendaItem):

    @browsing
    def test_agendaitem_without_attachements_has_no_documents(self, browser):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        browser.login().open(
            self.meeting_wrapper,
            view='agenda_items/{}/list'.format(item.agenda_item_id),
            data={'title': 'bar'})
        item = browser.json.get('items')[0]

        self.assertFalse(item.get('has_documents'))

    @browsing
    def test_agendaitem_with_attachements_has_documents(self, browser):
        item = self.setup_proposal(has_document = True)
        item = self.schedule_proposal(item, browser)

        browser.login().open(
            self.meeting_wrapper,
            view='agenda_items/{}/list'.format(item.agenda_item_id),
            data={'title': 'bar'})
        item = browser.json.get('items')[0]

        self.assertTrue(item.get('has_documents'))

    @browsing
    def test_agendaitem_with_excerpts_and_documents_has_documents(self, browser):
        self.setup_excerpt_template()
        item = self.setup_proposal(has_document = True)
        item = self.schedule_proposal(item, browser)
        browser.login().open(
            self.meeting_wrapper, {'_authenticator': createToken()},
            view='agenda_items/{}/decide'.format(item.agenda_item_id))

        browser.login().open(
            self.meeting_wrapper,
            view='agenda_items/{}/list'.format(item.agenda_item_id),
            data={'title': 'bar'})
        item = browser.json.get('items')[0]

        self.assertTrue(item.get('has_documents'))

    @browsing
    def test_agendaitem_with_excerpts_has_documents(self, browser):
        self.setup_excerpt_template()
        item = self.setup_proposal()
        item = self.schedule_proposal(item, browser)
        browser.login().open(
            self.meeting_wrapper, {'_authenticator': createToken()},
            view='agenda_items/{}/decide'.format(item.agenda_item_id))

        browser.login().open(
            self.meeting_wrapper,
            view='agenda_items/{}/list'.format(item.agenda_item_id),
            data={'title': 'bar'})
        item = browser.json.get('items')[0]

        self.assertTrue(item.get('has_documents'))


class TestAgendaItemEdit(TestAgendaItem):

    @browsing
    def test_update_agenda_item(self, browser):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        browser.login().open(
            self.meeting_wrapper,
            view='agenda_items/{}/edit'.format(item.agenda_item_id),
            data={'title': 'bar'})

        self.assertEqual(AgendaItem.get(item.agenda_item_id).title, 'bar')
        self.assertEquals([{u'message': u'Agenda Item updated.',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))
        self.assertEquals(True, browser.json.get('proceed'))

    @browsing
    def test_when_title_is_missing_returns_json_error(self, browser):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        browser.login().open(
            self.meeting_wrapper,
            view='agenda_items/{}/edit'.format(item.agenda_item_id))

        self.assertEquals([{u'message': u'Agenda Item title must not be empty.',
                            u'messageClass': u'error',
                            u'messageTitle': u'Error'}],
                          browser.json.get('messages'))
        self.assertEquals(False, browser.json.get('proceed'))

    @browsing
    def test_raises_not_found_for_invalid_agenda_item_id(self, browser):
        with self.assertRaises(NotFound):
            browser.login().open(self.meeting_wrapper,
                                 view='agenda_items/12345/edit')

    @browsing
    def test_update_agenda_item_raise_unauthorized_when_meeting_is_not_editable(self, browser):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        self.meeting.workflow_state = 'closed'

        with self.assertRaises(Unauthorized):
            browser.login().open(
                self.meeting_wrapper,
                view='agenda_items/{}/edit'.format(item.agenda_item_id),
                data={'title': 'bar'})


class TestAgendaItemDelete(TestAgendaItem):

    @browsing
    def test_delete_agenda_item(self, browser):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        browser.login().open(
            self.meeting_wrapper,
            view='agenda_items/{}/delete'.format(item.agenda_item_id))

        self.assertEquals(0, AgendaItem.query.count())
        self.assertEquals([{u'message': u'Agenda Item Successfully deleted',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))

    @browsing
    def test_raises_not_found_for_invalid_agenda_item_id(self, browser):
        with self.assertRaises(NotFound):
            browser.login().open(self.meeting_wrapper,
                                 view='agenda_items/12345/delete')

    @browsing
    def test_update_agenda_item_raise_unauthorized_when_meeting_is_not_editable(self, browser):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        self.meeting.workflow_state = 'closed'

        with self.assertRaises(Unauthorized):
            browser.login().open(
                self.meeting_wrapper,
                view='agenda_items/{}/delete'.format(item.agenda_item_id))


class TestAgendaItemDecide(TestAgendaItem):

    def test_meeting_is_held_when_deciding_an_agendaitem(self):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        item.decide()

        self.assertEquals('held', self.meeting.workflow_state)

    def test_decide_an_decided_agenda_item_is_ignored(self):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))
        item.decide()

        item.decide()

    @browsing
    def test_decide_agenda_item(self, browser):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        browser.login().open(
            self.meeting_wrapper,
            view='agenda_items/{}/decide'.format(item.agenda_item_id))

        self.assertEquals('decided', AgendaItem.query.first().workflow_state)
        self.assertEquals([{u'message': u'Agenda Item decided.',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))

    @browsing
    def test_decide_proposal_agenda_item(self, browser):
        self.setup_excerpt_template()
        proposal = self.setup_proposal()

        # schedule
        view = 'unscheduled_proposals/{}/schedule'.format(
            proposal.load_model().proposal_id)

        browser.login().open(self.meeting_wrapper, view=view)

        item = AgendaItem.query.first()
        browser.login().open(
            self.meeting_wrapper,
            view='agenda_items/{}/decide'.format(item.agenda_item_id),
            data={'_authenticator': createToken()})

        self.assertEquals('decided', AgendaItem.query.first().workflow_state)
        self.assertEquals(
            [{u'message': u'Agenda Item decided and excerpt generated.',
              u'messageClass': u'info',
              u'messageTitle': u'Information'}],
            browser.json.get('messages'))

    @browsing
    def test_raises_not_found_for_invalid_agenda_item_id(self, browser):
        with self.assertRaises(NotFound):
            browser.login().open(self.meeting_wrapper,
                                 view='agenda_items/12345/decide')

    @browsing
    def test_update_agenda_item_raise_unauthorized_when_meeting_is_not_editable(self, browser):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        self.meeting.workflow_state = 'closed'

        with self.assertRaises(Unauthorized):
            browser.login().open(
                self.meeting_wrapper,
                view='agenda_items/{}/decide'.format(item.agenda_item_id))

    @browsing
    def test_redirect_to_current_view_when_meeting_has_to_be_decided_as_well(self, browser):
        item1 = create(Builder('agenda_item')
                       .having(title=u'foo', meeting=self.meeting))
        item2 = create(Builder('agenda_item')
                       .having(title=u'foo', meeting=self.meeting))

        browser.login().open(
            self.meeting_wrapper,
            view='agenda_items/{}/decide'.format(item1.agenda_item_id))
        self.assertEquals(self.meeting_wrapper.absolute_url(),
                          browser.json.get('redirectUrl'))

        browser.login().open(
            self.meeting_wrapper,
            view='agenda_items/{}/decide'.format(item2.agenda_item_id))

        self.assertEquals(None, browser.json.get('redirectUrl'))


class TestAgendaItemUpdateOrder(TestAgendaItem):

    @browsing
    def test_update_agenda_item_order(self, browser):
        item1 = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting, sort_order=1))
        item2 = create(Builder('agenda_item').having(
            title=u'bar', meeting=self.meeting, sort_order=2))
        item3 = create(Builder('agenda_item').having(
            title=u'bar', meeting=self.meeting, sort_order=3))

        self.assertEqual(1, item1.sort_order)
        self.assertEqual(2, item2.sort_order)
        self.assertEqual(3, item3.sort_order)

        browser.login().open(self.meeting_wrapper,
                             view='agenda_items/update_order',
                             data={"sortOrder": json.dumps([1, 3, 2])})

        self.assertEqual(1, AgendaItem.get(1).sort_order)
        self.assertEqual(3, AgendaItem.get(2).sort_order)
        self.assertEqual(2, AgendaItem.get(3).sort_order)

        self.assertEquals([{u'message': u'Agenda Item order updated.',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))

    @browsing
    def test_raise_unauthorized_when_meeting_is_not_editable(self, browser):
        self.meeting.workflow_state = 'closed'

        with self.assertRaises(Unauthorized):
            browser.login().open(self.meeting_wrapper,
                                 view='agenda_items/update_order')


class TestScheduleParagraph(TestAgendaItem):

    @browsing
    def test_schedule_paragraph(self, browser):
        browser.login().open(self.meeting_wrapper,
                             view='agenda_items/schedule_paragraph',
                             data={'title': 'Abschnitt A'})

        agenda_items = Meeting.get(self.meeting.meeting_id).agenda_items

        self.assertEquals(1, len(agenda_items))
        self.assertEqual(u'Abschnitt A', agenda_items[0].title)
        self.assertTrue(agenda_items[0].is_paragraph)

    @browsing
    def test_raise_unauthorized_when_meeting_is_not_editable(self, browser):
        self.meeting.workflow_state = 'closed'

        with self.assertRaises(Unauthorized):
            browser.login().open(self.meeting_wrapper,
                                 view='agenda_items/schedule_paragraph')


class TestScheduleText(TestAgendaItem):

    @browsing
    def test_schedule_text(self, browser):
        browser.login().open(self.meeting_wrapper,
                             view='agenda_items/schedule_text',
                             data={'title': u'Baugesuch Herr Maier'})

        agenda_items = Meeting.get(self.meeting.meeting_id).agenda_items

        self.assertEquals(1, len(agenda_items))
        self.assertEqual(u'Baugesuch Herr Maier', agenda_items[0].title)
        self.assertFalse(agenda_items[0].is_paragraph)

    @browsing
    def test_raise_unauthorized_when_meeting_is_not_editable(self, browser):
        self.meeting.workflow_state = 'closed'

        with self.assertRaises(Unauthorized):
            browser.login().open(self.meeting_wrapper,
                                 view='agenda_items/schedule_paragraph')
