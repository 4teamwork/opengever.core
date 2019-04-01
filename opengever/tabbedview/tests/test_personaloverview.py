from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestPersonalOverview(IntegrationTestCase):

    @browsing
    def test_redirects_to_repository_root_on_a_foreign_admin_unit(
            self,
            browser,
        ):
        foreign_user = create(
            Builder('user')
            .named('Peter', 'Schneider')
            .with_roles('Reader'),
            )

        create(
            Builder('ogds_user')
            .id(foreign_user.getId())
            .having(firstname='Peter', lastname='Schneider'),
            )

        self.login(foreign_user, browser=browser)
        browser.open(self.portal, view='personal_overview')

        self.assertEqual(self.repository_root.absolute_url(), browser.url)

    @browsing
    def test_personal_overview_displays_username_in_title(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(view='personal_overview')

        self.assertEquals(
            u'Personal Overview: B\xe4rfuss K\xe4thi',
            browser.css('h1.documentFirstHeading').first.text,
            )

    @browsing
    def test_additional_tabs_are_shown_for_admins(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(view='personal_overview')

        expected_tabs = [
            'mydossiers',
            'mydocuments-proxy',
            'mytasks',
            'myissuedtasks',
            'alltasks',
            'allissuedtasks',
            ]

        self.assertEqual(expected_tabs, browser.css('li.formTab a').text)

    @browsing
    def test_additional_tabs_are_shown_for_inbox_users(self, browser):
        self.login(self.secretariat_user, browser=browser)
        browser.open(view='personal_overview')

        expected_tabs = [
            'mydossiers',
            'mydocuments-proxy',
            'mytasks',
            'myissuedtasks',
            'alltasks',
            'allissuedtasks',
            ]

        self.assertEqual(expected_tabs, browser.css('li.formTab a').text)

    @browsing
    def test_additional_tabs_are_hidden_for_regular_users(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(view='personal_overview')

        expected_tabs = [
            'mydossiers',
            'mydocuments-proxy',
            'mytasks',
            'myissuedtasks',
            ]

        self.assertEqual(expected_tabs, browser.css('li.formTab a').text)

    @browsing
    def test_notification_tab_is_hidden_when_activity_feature_is_disabled(
            self,
            browser,
        ):
        self.login(self.regular_user, browser=browser)
        browser.open(view='personal_overview')

        expected_tabs = [
            'mydossiers',
            'mydocuments-proxy',
            'mytasks',
            'myissuedtasks',
            ]

        self.assertEqual(expected_tabs, browser.css('li.formTab a').text)


class TestPersonalOverviewActivitySupport(IntegrationTestCase):

    features = ('activity', )

    @browsing
    def test_notification_tab_is_displayed_when_activity_feature_is_enabled(
            self,
            browser,
        ):
        self.login(self.secretariat_user, browser=browser)
        browser.open(view='personal_overview')

        expected_tabs = [
            'mydossiers',
            'mydocuments-proxy',
            'mytasks',
            'myissuedtasks',
            'My notifications',
            'alltasks',
            'allissuedtasks',
            ]

        self.assertEqual(expected_tabs, browser.css('li.formTab a').text)

        self.login(self.regular_user, browser=browser)
        browser.open(view='personal_overview')

        expected_tabs = [
            'mydossiers',
            'mydocuments-proxy',
            'mytasks',
            'myissuedtasks',
            'My notifications',
            ]

        self.assertEqual(expected_tabs, browser.css('li.formTab a').text)


class TestPersonalOverviewMeetingSupport(IntegrationTestCase):

    features = ('meeting', )

    @browsing
    def test_myproposal_tab_is_displayed_when_meeting_feature_is_enabled(
            self,
            browser,
        ):
        self.login(self.secretariat_user, browser=browser)
        browser.open(view='personal_overview')

        expected_tabs = [
            'mydossiers',
            'mydocuments-proxy',
            'mytasks',
            'myissuedtasks',
            'My proposals',
            'alltasks',
            'allissuedtasks',
            ]

        self.assertEqual(expected_tabs, browser.css('li.formTab a').text)


class TestGlobalTaskListings(IntegrationTestCase):

    @browsing
    def test_my_tasks_list_task_assigned_to_current_user(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(view='tabbedview_view-mytasks')
        expected_tasks = [
            u'F\xf6rw\xe4rding',
            u'Vertragsentwurf \xdcberpr\xfcfen',
            u'Mitarbeiter Dossier generieren',
            u'Personaleintritt',
            u'Vertragsentw\xfcrfe 2018',
            u'Status \xdcberpr\xfcfen',
            u'Ein notwendiges \xdcbel',
            u'Diskr\xe4te Dinge',
        ]
        found_tasks = [row.get('Title') for row in browser.css('.listing').first.dicts()]
        self.assertItemsEqual(expected_tasks, found_tasks)
        self.task.get_sql_object().responsible = 'robert.ziegler'
        browser.open(view='tabbedview_view-mytasks')
        expected_tasks = [
            u'F\xf6rw\xe4rding',
            u'Mitarbeiter Dossier generieren',
            u'Personaleintritt',
            u'Vertragsentw\xfcrfe 2018',
            u'Status \xdcberpr\xfcfen',
            u'Ein notwendiges \xdcbel',
            u'Diskr\xe4te Dinge',
            ]
        found_tasks = [row.get('Title') for row in browser.css('.listing').first.dicts()]

        self.assertItemsEqual(expected_tasks, found_tasks)

    @browsing
    def test_my_tasks_list_also_tasks_assigned_to_my_teams(self, browser):
        self.login(self.meeting_user, browser=browser)

        create(
            Builder('task')
            .within(self.dossier)
            .titled(u'Anfrage 1')
            .having(
                responsible_client='fa',
                responsible='team:1',
                issuer=self.dossier_responsible.getId(),
                task_type='correction',
                deadline=date(2016, 11, 1),
                )
            )

        create(
            Builder('task')
            .within(self.dossier)
            .titled(u'Anfrage 2')
            .having(
                responsible_client='fa',
                responsible='team:2',
                issuer=self.dossier_responsible.getId(),
                task_type='correction',
                deadline=date(2016, 11, 1),
                )
            )

        browser.open(view='tabbedview_view-mytasks')

        expected_tasks = [
            u'Anfrage 2',
            ]

        found_tasks = [
            row.get('Title')
            for row in browser.css('.listing').first.dicts()
            ]

        self.assertEquals(expected_tasks, found_tasks)

    @browsing
    def test_my_tasks_list_task_issued_by_the_current_user(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        browser.open(view='tabbedview_view-myissuedtasks')
        expected_tasks = [
            u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
            u'Vertragsentwurf \xdcberpr\xfcfen',
            u'Vertr\xe4ge abschliessen',
            u'Status \xdcberpr\xfcfen',
            u'Programm \xdcberpr\xfcfen',
            u'H\xf6rsaal reservieren',
            u'Diskr\xe4te Dinge',
            ]
        found_tasks = [row.get('Title') for row in browser.css('.listing').first.dicts()]
        self.assertEquals(expected_tasks, found_tasks)
        self.task.get_sql_object().issuer = 'kathi.barfuss'
        browser.open(view='tabbedview_view-myissuedtasks')
        expected_tasks = [
            u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
            u'Vertr\xe4ge abschliessen',
            u'Status \xdcberpr\xfcfen',
            u'Programm \xdcberpr\xfcfen',
            u'H\xf6rsaal reservieren',
            u'Diskr\xe4te Dinge',
            ]
        found_tasks = [row.get('Title') for row in browser.css('.listing').first.dicts()]
        self.assertEquals(expected_tasks, found_tasks)

    @browsing
    def test_all_task_list_all_task_assigned_to_current_org_unit(self, browser):
        self.login(self.secretariat_user, browser=browser)
        browser.open(view='tabbedview_view-alltasks')
        expected_tasks = [
            u'F\xf6rw\xe4rding',
            u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
            u'Vertragsentwurf \xdcberpr\xfcfen',
            u'Mitarbeiter Dossier generieren',
            u'Personaleintritt',
            u'Vertragsentw\xfcrfe 2018',
            u'Vertr\xe4ge abschliessen',
            u'Status \xdcberpr\xfcfen',
            u'Programm \xdcberpr\xfcfen',
            u'H\xf6rsaal reservieren',
            u'Diskr\xe4te Dinge',
            ]
        found_tasks = [row.get('Title') for row in browser.css('.listing').first.dicts()]
        self.assertItemsEqual(expected_tasks, found_tasks)
        self.task.get_sql_object().assigned_org_unit = 'additional'
        browser.open(view='tabbedview_view-alltasks')
        expected_tasks = [
            u'F\xf6rw\xe4rding',
            u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
            u'Mitarbeiter Dossier generieren',
            u'Personaleintritt',
            u'Vertragsentw\xfcrfe 2018',
            u'Vertr\xe4ge abschliessen',
            u'Status \xdcberpr\xfcfen',
            u'Programm \xdcberpr\xfcfen',
            u'H\xf6rsaal reservieren',
            u'Diskr\xe4te Dinge',
            ]
        found_tasks = [row.get('Title') for row in browser.css('.listing').first.dicts()]
        self.assertItemsEqual(expected_tasks, found_tasks)

    @browsing
    def test_all_issued_tasks_list_all_task_issued_by_the_current_org_unit(self, browser):
        self.login(self.secretariat_user, browser=browser)
        browser.open(view='tabbedview_view-allissuedtasks')
        expected_tasks = [
            u'F\xf6rw\xe4rding',
            u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
            u'Vertragsentwurf \xdcberpr\xfcfen',
            u'Mitarbeiter Dossier generieren',
            u'Personaleintritt',
            u'Vertragsentw\xfcrfe 2018',
            u'Vertr\xe4ge abschliessen',
            u'Status \xdcberpr\xfcfen',
            u'Programm \xdcberpr\xfcfen',
            u'H\xf6rsaal reservieren',
            u'Diskr\xe4te Dinge',
            ]
        found_tasks = [row.get('Title') for row in browser.css('.listing').first.dicts()]
        self.assertItemsEqual(expected_tasks, found_tasks)
        create(
            Builder('org_unit')
            .id('stv')
            .having(
                title=u'Steuerverwaltung',
                admin_unit_id='plone',
                )
            )

        self.task.get_sql_object().issuing_org_unit = 'stv'
        browser.open(view='tabbedview_view-allissuedtasks')
        expected_tasks = [
            u'F\xf6rw\xe4rding',
            u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
            u'Mitarbeiter Dossier generieren',
            u'Personaleintritt',
            u'Vertragsentw\xfcrfe 2018',
            u'Vertr\xe4ge abschliessen',
            u'Status \xdcberpr\xfcfen',
            u'Programm \xdcberpr\xfcfen',
            u'H\xf6rsaal reservieren',
            u'Diskr\xe4te Dinge',
        ]
        found_tasks = [row.get('Title') for row in browser.css('.listing').first.dicts()]
        self.assertItemsEqual(expected_tasks, found_tasks)
