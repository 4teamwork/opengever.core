from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.date_time import as_utc
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Proposal
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrasher
from plone.protect import createToken
from zope.component import getMultiAdapter
import json
import pytz
import re


class TestDisplayAgendaItems(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_agendaitem_without_attachements_has_no_documents(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_ad_hoc(self.meeting, 'Foo')

        browser.open(self.agenda_item_url(agenda_item, 'list'))
        item = browser.json.get('items')[0]
        self.assertFalse(item.get('has_documents'))

    @browsing
    def test_agendaitem_with_attachements_has_documents(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)

        browser.open(self.agenda_item_url(agenda_item, 'list'))
        item = browser.json.get('items')[0]
        self.assertTrue(item.get('has_documents'))

    @browsing
    def test_agendaitem_attachements_are_sorted_by_position_in_relation_field(self, browser):
        self.login(self.committee_responsible, browser)
        documents = [
            create(Builder('document')
                   .within(self.dossier)
                   .titled(title))
            for title in ('Doc 1', 'Doc 4', 'Doc 2', 'Doc 3')
        ]
        documents.reverse()

        self.dossier.moveObjectToPosition(documents[1].getId(), 0)

        proposal, submitted_proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .having(committee=self.committee.load_model())
                          .with_submitted()
                          .relate_to(*documents))
        agenda_item = self.schedule_proposal(self.meeting, submitted_proposal)

        browser.open(self.agenda_item_url(agenda_item, 'list'))
        item = browser.json.get('items')[0]
        self.assertTrue(item.get('has_documents'))

        pattern = re.compile('<a class="document_link.*?>(.*?)</a>')
        browser_titles = [pattern.search(el).groups()[0] for el in item.get('documents')]
        self.assertEquals([u'Doc 3', 'Doc 2', 'Doc 4', 'Doc 1'],
                          browser_titles)

    @browsing
    def test_agendaitem_with_excerpts_and_documents_has_documents(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        agenda_item.decide()
        agenda_item.generate_excerpt('excerpt')

        browser.open(self.agenda_item_url(agenda_item, 'list'))
        item = browser.json.get('items')[0]

        self.assertTrue(item.get('has_documents'))

    @browsing
    def test_agendaitem_sorts_excerpts_alphabetically(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
        agenda_item.decide()
        agenda_item.generate_excerpt('b excerpt')
        agenda_item.generate_excerpt('c excerpt')
        agenda_item.generate_excerpt('a excerpt')

        excerpts = browser.open(self.agenda_item_url(agenda_item, 'list')).json.get('items')[0].get('excerpts')
        excerpt_links = ' '.join([excerpt.get('link') for excerpt in excerpts])

        browser.open_html(excerpt_links)

        expected_excerpt_order = ['a excerpt', 'b excerpt', 'c excerpt']
        excerpt_order = browser.open_html(excerpt_links).css('a').text
        self.assertEqual(excerpt_order, expected_excerpt_order)

    @browsing
    def test_trashed_exceprts_are_not_listed_for_agendaitem(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
        agenda_item.decide()
        excerpt1 = agenda_item.generate_excerpt('excerpt 1')
        agenda_item.generate_excerpt('excerpt 2')

        excerpts = browser.open(self.agenda_item_url(agenda_item, 'list')).json.get('items')[0].get('excerpts')
        self.assertEqual(len(excerpts), 2)

        ITrasher(excerpt1).trash()
        excerpts = browser.open(self.agenda_item_url(agenda_item, 'list')).json.get('items')[0].get('excerpts')
        self.assertEqual(len(excerpts), 1)

        excerpt_links = ' '.join([excerpt.get('link') for excerpt in excerpts])
        excerpt_titles = browser.open_html(excerpt_links).css('a').text
        self.assertEqual(['excerpt 2'], excerpt_titles)

    @browsing
    def test_trashed_exceprts_are_not_listed_for_ad_hoc_agendaitem(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_ad_hoc(self.meeting, 'Foo')
        agenda_item.decide()
        excerpt1 = agenda_item.generate_excerpt('excerpt 1')
        agenda_item.generate_excerpt('excerpt 2')

        excerpts = browser.open(self.agenda_item_url(agenda_item, 'list')).json.get('items')[0].get('excerpts')
        self.assertEqual(len(excerpts), 2)

        ITrasher(excerpt1).trash()
        excerpts = browser.open(self.agenda_item_url(agenda_item, 'list')).json.get('items')[0].get('excerpts')
        self.assertEqual(len(excerpts), 1)

        excerpt_links = ' '.join([excerpt.get('link') for excerpt in excerpts])
        excerpt_titles = browser.open_html(excerpt_links).css('a').text
        self.assertEqual(['excerpt 2'], excerpt_titles)


class TestEditAgendaItems(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_update_agenda_item(self, browser):
        self.login(self.committee_responsible, browser)

        agenda_item = self.schedule_ad_hoc(self.meeting, 'hax')
        browser.open(self.agenda_item_url(agenda_item, 'edit'),
                     data={'title': u'b\xe4r',
                           'description': u'f\xf6o'})

        self.assertEqual(agenda_item.title, u'b\xe4r')
        self.assertEqual(agenda_item.description, u'f\xf6o')
        self.assertEquals([{u'message': u'Agenda Item updated.',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))
        self.assertEquals(True, browser.json.get('proceed'))

    @browsing
    def test_updating_agenda_item_will_update_modification_dates(self, browser):
        self.login(self.committee_responsible, browser)
        model = self.meeting.model

        creation_date = datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)
        update_date = datetime(2018, 10, 16, 0, 0, tzinfo=pytz.utc)

        def generate_agendaitem_list(meeting):
            meeting_view = getMultiAdapter(
                (self.meeting, self.request), name='view')
            browser.open(meeting_view.url_generate_agendaitem_list())

        # Generate first protocol
        with freeze(creation_date):
            generate_agendaitem_list(self.meeting)

        document = model.agendaitem_list_document.resolve_document()

        self.assertEqual(creation_date, as_utc(document.modified().asdatetime()))
        self.assertEqual(creation_date, document.changed)

        # Update the protocol
        with freeze(update_date):
            generate_agendaitem_list(self.meeting)

        self.assertEqual(update_date, as_utc(document.modified().asdatetime()))
        self.assertEqual(update_date, document.changed)

    @browsing
    def test_display_changed_property_as_last_modified_date(self, browser):
        self.login(self.committee_responsible, browser)
        model = self.meeting.model

        creation_date = datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)
        update_date = datetime(2018, 10, 16, 0, 0, tzinfo=pytz.utc)

        def generate_agendaitem_list(meeting):
            meeting_view = getMultiAdapter(
                (self.meeting, self.request), name='view')
            browser.open(meeting_view.url_generate_agendaitem_list())

        # Generate first protocol
        with freeze(creation_date):
            generate_agendaitem_list(self.meeting)

        document = model.agendaitem_list_document.resolve_document()
        document.changed = update_date
        document.reindexObject(idxs=["changed"])

        self.assertEqual(creation_date, as_utc(document.modified().asdatetime()))
        self.assertEqual(update_date, document.changed)

        browser.open(self.meeting)

        self.assertEqual(
            'Modified at Oct 16, 2018 02:00 AM',
            browser.css('.agenda-item-list-doc .document-modified').first.text)

    @browsing
    def test_when_title_is_missing_returns_json_error(self, browser):
        self.login(self.committee_responsible, browser)

        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        browser.open(self.agenda_item_url(agenda_item, 'edit'), data={})

        self.assertEquals([{u'message': u'Agenda Item title must not be empty.',
                            u'messageClass': u'error',
                            u'messageTitle': u'Error'}],
                          browser.json.get('messages'))
        self.assertEquals(True, browser.json.get('proceed'))

    @browsing
    def test_when_title_is_too_long_returns_json_error(self, browser):
        self.login(self.committee_responsible, browser)

        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        browser.open(self.agenda_item_url(agenda_item, 'edit'),
                     data={'title': 257 * u'a'})

        self.assertEquals([{u'message': u'Agenda Item title is too long.',
                            u'messageClass': u'error',
                            u'messageTitle': u'Error'}],
                          browser.json.get('messages'))
        self.assertEquals(True, browser.json.get('proceed'))

    @browsing
    def test_raises_not_found_for_invalid_agenda_item_id(self, browser):
        self.login(self.committee_responsible, browser)

        with browser.expect_http_error(404):
            browser.open(self.meeting,
                                 view='agenda_items/12345/edit')

    @browsing
    def test_update_agenda_item_raise_forbidden_when_meeting_is_not_editable(self, browser):
        self.login(self.committee_responsible, browser)

        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        self.decide_agendaitem_generate_and_return_excerpt(agenda_item)
        self.meeting.model.close()

        with browser.expect_http_error(code=403):
            browser.open(self.agenda_item_url(agenda_item, 'edit'),
                         data={'title': 'qux'})


class TestDeleteAgendaItems(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_delete_agenda_item(self, browser):
        self.login(self.committee_responsible, browser)

        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        self.assert_workflow_state('proposal-state-scheduled', self.proposal)
        browser.open(self.agenda_item_url(agenda_item, 'delete'))

        self.assertEquals([{u'message': u'Agenda Item Successfully deleted',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))
        self.assert_workflow_state('proposal-state-submitted', self.proposal)

    @browsing
    def test_raises_not_found_for_invalid_agenda_item_id(self, browser):
        self.login(self.committee_responsible, browser)

        with browser.expect_http_error(404):
            browser.open(self.meeting,
                         view='agenda_items/12345/delete')

    @browsing
    def test_raise_not_found_if_agenda_item_is_not_linked_to_the_given_context(self, browser):
        self.login(self.committee_responsible, browser)

        # create a new meeting with an agenda item
        other_meeting = create(Builder('meeting')
                               .having(committee=self.committee.load_model())
                               .link_with(self.meeting_dossier))
        other_item = create(Builder('agenda_item').having(
            title=u'foo', meeting=other_meeting))

        with browser.expect_http_error(reason='Not Found'):
            browser.open(
                self.meeting,
                view='agenda_items/{}/delete'.format(other_item.agenda_item_id))

    @browsing
    def test_update_agenda_item_raise_forbidden_when_agenda_list_is_not_editable(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)

        self.meeting.model.hold()

        with browser.expect_http_error(code=403):
            browser.open(self.agenda_item_url(agenda_item, 'delete'))

    @browsing
    def test_delete_handles_already_trashed_documents(self, browser):
        self.login(self.committee_responsible, browser)

        agenda_item = self.schedule_ad_hoc(self.meeting, 'Gugus')
        doc = agenda_item.resolve_document()
        ITrasher(doc).trash()

        browser.open(self.agenda_item_url(agenda_item, 'delete'))
        self.assertEquals([{u'message': u'Agenda Item Successfully deleted',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))


class TestDecideAgendaItem(IntegrationTestCase):

    features = ('meeting',)

    def test_meeting_is_held_when_deciding_an_agendaitem(self):
        self.login(self.committee_responsible)

        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        agenda_item.decide()

        self.assertEquals('held', self.meeting.model.workflow_state)

    def test_decide_an_decided_agenda_item_is_ignored(self):
        self.login(self.committee_responsible)
        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)

        agenda_item.decide()
        agenda_item.decide()

    @browsing
    def test_raises_not_found_for_invalid_agenda_item_id(self, browser):
        self.login(self.committee_responsible, browser)

        with browser.expect_http_error(404):
            browser.open(self.meeting,
                         view='agenda_items/12345/decide')

    @browsing
    def test_redirect_to_current_view_when_meeting_has_to_be_decided_as_well(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item_1 = self.schedule_ad_hoc(self.meeting, 'Gugus')
        agenda_item_2 = self.schedule_ad_hoc(self.meeting, 'Kux')

        browser.open(self.agenda_item_url(agenda_item_1, 'decide'),
                     data={'_authenticator': createToken()})
        self.assertEquals(self.meeting.absolute_url(),
                          browser.json.get('redirectUrl'))

        browser.open(self.agenda_item_url(agenda_item_2, 'decide'),
                     data={'_authenticator': createToken()})
        self.assertEquals(None, browser.json.get('redirectUrl'))


class TestReopenAgendaItem(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_reopen_agenda_item(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        self.decide_agendaitem_generate_and_return_excerpt(agenda_item)

        browser.open(self.agenda_item_url(agenda_item, 'reopen'),
                     data={'_authenticator': createToken()})

        self.assertEquals(AgendaItem.STATE_REVISION,
                          agenda_item.get_state())
        self.assertEquals(Proposal.STATE_DECIDED,
                          agenda_item.proposal.get_state())
        self.assertEquals([{u'message': u'Agenda Item successfully reopened.',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))

    @browsing
    def test_raises_not_found_for_invalid_agenda_item_id(self, browser):
        self.login(self.committee_responsible, browser)

        with browser.expect_http_error(404):
            browser.open(self.meeting,
                         view='agenda_items/98765/reopen')

    @browsing
    def test_raise_forbidden_when_meeting_is_not_editable(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        self.decide_agendaitem_generate_and_return_excerpt(agenda_item)
        self.meeting.model.close()

        with browser.expect_http_error(code=403):
            browser.open(self.agenda_item_url(agenda_item, 'reopen'),
                         data={'_authenticator': createToken()})


class TestReviseAgendaItem(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_revise_agenda_item(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        self.decide_agendaitem_generate_and_return_excerpt(agenda_item)
        agenda_item.reopen()

        browser.open(self.agenda_item_url(agenda_item, 'revise'),
                     data={'_authenticator': createToken()})

        self.assertEquals(AgendaItem.STATE_DECIDED,
                          agenda_item.get_state())
        self.assertEquals(Proposal.STATE_DECIDED,
                          agenda_item.proposal.get_state())
        self.assertEquals([{u'message': u'Agenda Item revised successfully.',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))

    @browsing
    def test_raises_not_found_for_invalid_agenda_item_id(self, browser):
        self.login(self.committee_responsible, browser)

        with browser.expect_http_error(404):
            browser.open(self.meeting,
                         view='agenda_items/98761/revise')

    @browsing
    def test_raise_forbidden_when_meeting_is_not_editable(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        self.decide_agendaitem_generate_and_return_excerpt(agenda_item)
        self.meeting.model.close()

        with browser.expect_http_error(code=403):
            browser.open(self.agenda_item_url(agenda_item, 'revise'),
                         data={'_authenticator': createToken()})


class TestUpdateAgendaItemOrder(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_update_agenda_item_order(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item_1 = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        agenda_item_2 = self.schedule_ad_hoc(
            self.meeting, u'Zw\xf6i')
        agenda_item_3 = self.schedule_ad_hoc(
            self.meeting, u'Fine')

        self.assertEqual(1, agenda_item_1.sort_order)
        self.assertEqual(2, agenda_item_2.sort_order)
        self.assertEqual(3, agenda_item_3.sort_order)

        new_order = [
            agenda_item_1.agenda_item_id,
            agenda_item_3.agenda_item_id,
            agenda_item_2.agenda_item_id,
        ]
        browser.open(self.meeting,
                     view='agenda_items/update_order',
                     data={"sortOrder": json.dumps(new_order)})

        self.assertEqual(1, agenda_item_1.sort_order)
        self.assertEqual(3, agenda_item_2.sort_order)
        self.assertEqual(2, agenda_item_3.sort_order)

        self.assertEquals([{u'message': u'Agenda Item order updated.',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))

    @browsing
    def test_raise_forbidden_when_meeting_is_closed(self, browser):
        self.login(self.committee_responsible, browser)
        self.meeting.model.close()

        with browser.expect_http_error(code=403):
            browser.open(self.meeting,
                                 view='agenda_items/update_order')

    @browsing
    def test_raise_forbidden_when_meeting_is_held(self, browser):
        self.login(self.committee_responsible, browser)
        self.meeting.model.hold()

        with browser.expect_http_error(code=403):
            browser.open(self.meeting,
                                 view='agenda_items/update_order')


class TestScheduleParagraph(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_schedule_paragraph(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting,
                             view='agenda_items/schedule_paragraph',
                             data={'title': u'\xc4bschnitt A',
                                   'description': u'B\xe4schreibung'})

        agenda_items = self.meeting.model.agenda_items
        self.assertEquals(1, len(agenda_items))
        self.assertEqual(u'\xc4bschnitt A', agenda_items[0].title)
        self.assertEqual(u'B\xe4schreibung', agenda_items[0].description)
        self.assertTrue(agenda_items[0].is_paragraph)

    @browsing
    def test_raise_forbidden_when_meeting_is_held(self, browser):
        self.login(self.committee_responsible, browser)
        self.meeting.model.hold()

        with browser.expect_http_error(code=403):
            browser.open(self.meeting,
                                 view='agenda_items/schedule_paragraph',
                                 data={'title': u'\xc4bschnitt A',
                                       'description': u'B\xe4schreibung'})

    @browsing
    def test_raise_forbidden_when_meeting_is_closed(self, browser):
        self.login(self.committee_responsible, browser)
        self.meeting.model.close()

        with browser.expect_http_error(code=403):
            browser.open(self.meeting,
                                 view='agenda_items/schedule_paragraph',
                                 data={'title': u'\xc4bschnitt A',
                                       'description': u'B\xe4schreibung'})


class TestScheduleText(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_raise_forbidden_when_meeting_is_held(self, browser):
        self.login(self.committee_responsible, browser)
        self.meeting.model.hold()

        with browser.expect_http_error(code=403):
            browser.open(self.meeting,
                                 view='agenda_items/schedule_text',
                                 data={'title': u'Baugesuch Herr Maier'})

    @browsing
    def test_raise_forbidden_when_meeting_is_closed(self, browser):
        self.login(self.committee_responsible, browser)
        self.meeting.model.close()

        with browser.expect_http_error(code=403):
            browser.open(self.meeting,
                                 view='agenda_items/schedule_text',
                                 data={'title': u'Baugesuch Herr Maier'})
