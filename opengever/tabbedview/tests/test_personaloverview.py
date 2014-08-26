from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import create_plone_user
from opengever.testing import FunctionalTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
import transaction


class TestPersonalOverview(FunctionalTestCase):

    def setUp(self):
        super(TestPersonalOverview, self).setUp()

        create_plone_user(self.portal, 'hugo.boss')
        self.hugo = create(Builder('ogds_user')
                           .having(userid='hugo.boss',
                                   firstname='Hugo',
                                   lastname='Boss')
                           .assign_to_org_units([self.org_unit]))
        transaction.commit()

    @browsing
    def test_redirects_to_repository_root_on_a_foreign_admin_unit(self, browser):
        create_plone_user(self.portal, 'peter')
        setRoles(self.portal, 'hugo.boss', ['Reader'])
        transaction.commit()

        additional = create(Builder('org_unit')
                            .id('additional')
                            .with_default_groups())
        admin_unit = create(Builder('admin_unit')
                            .id('additional')
                            .assign_org_units([additional]))

        self.hugo = create(Builder('ogds_user')
                           .having(userid='peter')
                           .assign_to_org_units([additional]))

        repo_root = create(Builder('repository_root'))

        browser.login(username='peter', password='demo09').open(
            view='personal_overview')
        self.assertEqual(repo_root.absolute_url(), browser.url)

    @browsing
    def test_personal_overview_displays_username_in_title(self, browser):
        browser.login().open(view='personal_overview')
        self.assertEquals(u'Personal Overview: Test User',
                          browser.css('h1.documentFirstHeading').first.text)

    @browsing
    def test_additional_tabs_are_shown_for_admins(self, browser):
        setRoles(self.portal, 'hugo.boss', ['Administrator'])
        transaction.commit()

        browser.login(username='hugo.boss', password='demo09').open(
            view='personal_overview')
        self.assertEqual(
            ['mydossiers', 'mydocuments', 'mytasks', 'myissuedtasks',
             'alltasks', 'allissuedtasks'],
            browser.css('li.formTab a').text)

    @browsing
    def test_additional_tabs_are_shown_for_inbox_users(self, browser):
        browser.login().open(view='personal_overview')
        self.assertEqual(
            ['mydossiers', 'mydocuments', 'mytasks', 'myissuedtasks',
             'alltasks', 'allissuedtasks'],
            browser.css('li.formTab a').text)

    @browsing
    def test_additional_tabs_are_hidden_for_regular_users(self, browser):
        setRoles(self.portal, 'hugo.boss', ['Reader'])
        browser.login(username='hugo.boss', password='demo09').open(
            view='personal_overview')
        self.assertEqual(
            ['mydossiers', 'mydocuments', 'mytasks', 'myissuedtasks'],
            browser.css('li.formTab a').text)


class TestGlobalTaskListings(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestGlobalTaskListings, self).setUp()

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        self.hugo = create(Builder('ogds_user')
                           .having(userid='hugo.boss',
                                   firstname='Hugo',
                                   lastname='Boss')
                           .assign_to_org_units([self.org_unit]))

        self.task1 = create(Builder('task')
                            .having(responsible_client='client1',
                                    responsible=TEST_USER_ID,
                                    issuer=TEST_USER_ID))
        self.task2 = create(Builder('task')
                            .having(responsible_client='client2',
                                    responsible='hugo.boss',
                                    issuer=TEST_USER_ID))
        self.task3 = create(Builder('task')
                            .having(responsible_client='client1',
                                    responsible=TEST_USER_ID,
                                    issuer='hugo.boss'))

    def test_my_tasks(self):
        view = self.portal.unrestrictedTraverse(
            'tabbedview_view-mytasks')
        view.update()

        self.assertEquals(
            [self.task1.get_sql_object(), self.task3.get_sql_object()],
            view.contents)

    def test_my_issued_tasks(self):
        view = self.portal.unrestrictedTraverse(
            'tabbedview_view-myissuedtasks')
        view.update()

        self.assertEquals(
            [self.task1.get_sql_object(), self.task2.get_sql_object()],
            view.contents)

    def test_all_tasks(self):
        view = self.portal.unrestrictedTraverse(
            'tabbedview_view-alltasks')
        view.update()

        expected = [self.task1, self.task3]
        self.assertEquals(
            [task.get_sql_object() for task in expected],
            view.contents)

    def test_all_issued_tasks(self):
        view = self.portal.unrestrictedTraverse(
            'tabbedview_view-allissuedtasks')
        view.update()

        expected = [self.task1, self.task2, self.task3]
        self.assertEquals(
            [task.get_sql_object() for task in expected],
            view.contents)
