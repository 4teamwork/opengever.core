from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import FormFieldNotFound
from opengever.base.oguid import Oguid
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.testing import FunctionalTestCase


class TestCommittee(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    group_field_name = 'Group'

    def setUp(self):
        super(TestCommittee, self).setUp()
        self.repo_root = create(Builder('repository_root'))
        self.repository_folder = create(Builder('repository')
                                        .within(self.repo_root)
                                        .titled('Repo'))
        self.container = create(Builder('committee_container'))

    def test_committee_can_be_added(self):
        committee = create(Builder('committee').within(self.container))
        self.assertEqual('committee-1', committee.getId())

        model = committee.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(committee), model.oguid)

    @browsing
    def test_committee_can_be_created_in_browser(self, browser):
        self.grant('Administrator')
        browser.login()
        browser.open(self.container, view='++add++opengever.meeting.committee')

        browser.fill(
            {'Title': u'A c\xf6mmittee',
             'Linked repository folder': self.repository_folder,
             self.group_field_name: 'client1_users'})
        browser.css('#form-buttons-save').first.click()

        browser.fill({'Title': u'Initial',
                      'Start date': 'January 1, 2012',
                      'End date': 'December 31, 2012'}).submit()

        self.assertIn('Item created',
                      browser.css('.portalMessage.info dd').text)

        committee = browser.context
        self.assertEqual('committee-1', committee.getId())
        self.assertEqual(
            ('CommitteeGroupMember',),
            dict(committee.get_local_roles()).get('client1_users'))

        model = committee.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(committee), model.oguid)
        self.assertEqual(u'A c\xf6mmittee', model.title)

        self.assertEqual(1, len(model.periods))
        period = model.periods[0]
        self.assertEqual('active', period.workflow_state)
        self.assertEqual(u'Initial', period.title)
        self.assertEqual(date(2012, 1, 1), period.date_from)
        self.assertEqual(date(2012, 12, 31), period.date_to)

    @browsing
    def test_committee_can_be_edited_in_browser(self, browser):
        self.grant('Administrator')
        committee = create(Builder('committee')
                           .within(self.container)
                           .titled(u'My Committee')
                           .link_with(self.repository_folder))

        self.assertEqual(
            ('CommitteeGroupMember',),
            dict(committee.get_local_roles()).get('client1_users'))

        browser.login().visit(committee, view='edit')
        form = browser.css('#content-core form').first

        self.assertEqual(u'My Committee', form.find_field('Title').value)

        browser.fill({'Title': u'A c\xf6mmittee',
                      self.group_field_name: u'client1_inbox_users'})
        browser.css('#form-buttons-save').first.click()
        self.assertIn('Changes saved',
                      browser.css('.portalMessage.info dd').text)

        committee = browser.context
        self.assertEqual('committee-1', committee.getId())
        local_roles = dict(committee.get_local_roles())
        self.assertNotIn('client1_users', local_roles,
                         local_roles.get('client1_users'))
        self.assertEqual(
            ('CommitteeGroupMember',),
            local_roles.get('client1_inbox_users'))

        model = committee.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(u'A c\xf6mmittee', model.title)

    @browsing
    def test_committee_group_is_not_editable_for_users_with_missing_permission(self, browser):
        user = create(Builder('user')
                      .named('Hugo', 'Boss')
                      .in_groups('client1_users'))
        committee = create(Builder('committee')
                           .within(self.container)
                           .titled(u'My Committee')
                           .having(group_id='client1_users')
                           .link_with(self.repository_folder))

        browser.login(username='hugo.boss').visit(committee, view='edit')
        with self.assertRaises(FormFieldNotFound):
            browser.fill({self.group_field_name: 'client1_users'})
