from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.oguid import Oguid
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.model import Committee
from opengever.testing import FunctionalTestCase
import transaction


class TestCommittee(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    group_field_name = 'Group'

    def setUp(self):
        super(TestCommittee, self).setUp()
        self.repo_root = create(Builder('repository_root'))
        self.repository_folder = create(Builder('repository')
                                        .within(self.repo_root)
                                        .titled('Repo'))
        self.template = create(Builder('sablontemplate'))
        self.container = create(Builder('committee_container')
                                .having(toc_template=self.template))

    def test_committee_can_be_added(self):
        committee = create(Builder('committee').within(self.container))
        self.assertEqual('committee-1', committee.getId())

        model = committee.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(committee), model.oguid)

    def test_get_toc_template_returns_committee_template_if_available(self):
        committee = create(
            Builder('committee')
            .having(toc_template=self.template)
            .within(self.container))
        self.assertEqual(self.template, committee.get_toc_template())

    def test_get_toc_template_falls_back_to_container(self):
        committee = create(Builder('committee').within(self.container))
        self.assertEqual(self.template, committee.get_toc_template())

    @browsing
    def test_committee_repository_is_validated(self, browser):
        parent_repo = create(Builder('repository')
                             .within(self.repo_root))
        leaf_repo = create(Builder('repository')
                           .within(parent_repo))

        self.grant('Administrator')
        browser.login()
        browser.open(self.container, view='++add++opengever.meeting.committee')

        browser.fill(
            {'Title': u'A c\xf6mmittee',
             'Linked repository folder': parent_repo,
             self.group_field_name: 'client1_users'})
        browser.css('#form-buttons-save').first.click()

        error = browser.css("#formfield-form-widgets-repository_folder div.error").first.text
        self.assertEqual('You cannot add dossiers in the selected repository '
                         'folder. Either you do not have the privileges or '
                         'the repository folder contains another repository '
                         'folder.',
                         error)

    @browsing
    def test_committee_can_be_created_in_browser(self, browser):
        self.grant('Administrator')

        templates = create(Builder('templatefolder'))
        sablon_template = create(
            Builder('sablontemplate')
            .within(templates)
            .with_asset_file('sablon_template.docx'))

        browser.login()
        browser.open(self.container, view='++add++opengever.meeting.committee')

        browser.fill(
            {'Title': u'A c\xf6mmittee',
             'Protocol template': sablon_template,
             'Excerpt template': sablon_template,
             'Table of contents template': sablon_template,
             'Linked repository folder': self.repository_folder,
             self.group_field_name: 'client1_users'})
        browser.css('#form-buttons-save').first.click()

        browser.fill({'Title': u'Initial',
                      'Start date': '01.01.2012',
                      'End date': '31.12.2012'}).submit()

        self.assertIn('Item created',
                      browser.css('.portalMessage.info dd').text)

        committee = browser.context
        self.assertEqual('committee-1', committee.getId())
        self.assertEqual(
            ('CommitteeGroupMember',),
            dict(committee.get_local_roles()).get('client1_users'))
        self.assertEqual(self.repository_folder,
                         committee.get_repository_folder())
        self.assertEqual(sablon_template, committee.get_protocol_template())
        self.assertEqual(sablon_template, committee.get_excerpt_template())

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


class TestCommitteeWorkflow(FunctionalTestCase):

    def test_initial_state_is_active(self):
        committee = create(Builder('committee').titled(u'My Committee'))
        self.assertEqual(Committee.STATE_ACTIVE,
                         committee.load_model().get_state())

    @browsing
    def test_can_be_deactivated(self, browser):
        committee = create(Builder('committee').titled(u'My Committee'))

        browser.login().open(committee)
        browser.find('Deactivate').click()

        self.assertEqual(Committee.STATE_INACTIVE,
                         committee.load_model().get_state())
        self.assertEqual(['Committee deactivated successfully'],
                         info_messages())

    @browsing
    def test_deactivating_is_not_possible_when_pending_meetings_exists(self, browser):
        committee = create(Builder('committee').titled(u'My Committee'))
        create(Builder('meeting').having(committee=committee))

        browser.login().open(committee)
        browser.find('Deactivate').click()

        self.assertEqual(['Not all meetings are closed.'], error_messages())
        self.assertEqual(Committee.STATE_ACTIVE,
                         committee.load_model().get_state())

    @browsing
    def test_when_unscheduled_proposals_exist(self, browser):
        repo = create(Builder('repository'))
        dossier = create(Builder('dossier').within(repo))
        committee = create(Builder('committee').titled(u'My Committee'))
        proposal = create(Builder('proposal')
                          .within(dossier)
                          .having(committee=committee.load_model())
                          .as_submitted())

        browser.login().open(committee)
        browser.find('Deactivate').click()

        self.assertEqual(
            ['There are unscheduled proposals submitted to this committee.'],
            error_messages())
        self.assertEqual(Committee.STATE_ACTIVE,
                         committee.load_model().get_state())

    @browsing
    def test_deactivated_comittee_can_be_reactivated(self, browser):
        committee = create(Builder('committee')
                           .titled(u'My Committee'))

        committee.load_model().deactivate()
        transaction.commit()

        browser.login().open(committee)
        browser.find('Activate').click()

        self.assertEqual(Committee.STATE_ACTIVE,
                         committee.load_model().get_state())
        self.assertEqual(['Committee reactivated successfully'],
                         info_messages())

    @browsing
    def test_add_meeting_is_not_available_on_inactive_committee(self, browser):
        committee = create(Builder('committee')
                           .titled(u'My Committee'))

        committee.load_model().deactivate()
        transaction.commit()

        browser.login().open(committee)
        self.assertEqual(
            [],
            browser.css('#plone-contentmenu-factories #add-meeting'))

    @browsing
    def test_add_membership_is_not_available_on_inactive_committee(self, browser):
        committee = create(Builder('committee')
                           .titled(u'My Committee'))

        committee.load_model().deactivate()
        transaction.commit()

        browser.login().open(committee)
        self.assertEqual(
            [],
            browser.css('#plone-contentmenu-factories #add-membership'))
