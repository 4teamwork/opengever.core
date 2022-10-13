from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from opengever.webactions.storage import get_storage
from plone.app.testing import TEST_USER_ID
from urllib import urlencode


class TestActionmenuViewlet(FunctionalTestCase):

    def setUp(self):
        super(TestActionmenuViewlet, self).setUp()

        create(Builder('ogds_user').id('hugo.boss'))
        dossier = create(Builder('dossier'))
        self.task = create(Builder('task')
                           .within(dossier)
                           .having(issuer='hugo.boss',
                                   responsible=TEST_USER_ID,
                                   task_type='comment'))

    @browsing
    def test_action_menu_viewlet(self, browser):
        browser.login().open(self.task, view='tabbedview_view-overview')
        self.assertGreater(len(browser.css('#action-menu li')), 1,
                           'no action menu entries found')

    @browsing
    def test_agency_actions_are_display_separately(self, browser):
        browser.login().open(self.task, view='tabbedview_view-overview')

        self.assertEquals(
            ['Modify deadline',
             'Accept',
             'Reject',
             'Resolve',
             'Reassign',
             'label_add_comment'],
            browser.css('ul.regular_buttons a').text)

        self.assertEquals(
            ['Cancel',
             'Close'],
            browser.css('dl.agency_buttons ul a').text)

    @browsing
    def test_agency_button_is_hidden_when_no_agency_actions_are_available(self, browser):
        task = create(Builder('task')
                           .having(issuer=TEST_USER_ID,
                                   responsible=TEST_USER_ID,
                                   task_type='comment'))

        browser.login().open(task, view='tabbedview_view-overview')

        self.assertEquals([], browser.css('dl.agency_buttons'))


class TestActionmenuViewletWebactions(IntegrationTestCase):

    def setUp(self):
        super(TestActionmenuViewletWebactions, self).setUp()

        create(Builder('webaction')
               .titled(u'Action 1')
               .having(order=5,
                       display='action-buttons',
                       icon_name="fa-helicopter"))

        create(Builder('webaction')
               .titled(u'Action 2')
               .having(order=1,
                       display='action-buttons',
                       target_url="http://example.org/endpoint2"))

    @browsing
    def test_webactions_display(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.task, view='tabbedview_view-overview')

        webactions = browser.css('ul.webactions_buttons a')
        self.assertEqual(2, len(webactions))
        self.assertEqual(['Action 2', 'Action 1'], webactions.text)

        params = urlencode({'context': self.task.absolute_url(), 'orgunit': 'fa'})
        self.assertEqual(map(lambda item: item.get("href"), webactions),
                         ['http://example.org/endpoint2?{}'.format(params),
                          'http://example.org/endpoint?{}'.format(params)])

        self.assertEqual(
            map(lambda item: item.get("class"), webactions),
            ['webaction_button', 'webaction_button fa fa-helicopter'])

    @browsing
    def test_only_webactions_with_display_actions_buttons_are_displayed(self, browser):
        self.login(self.regular_user, browser)
        storage = get_storage()
        storage.update(0, {"display": "title-buttons"})

        browser.open(self.task, view='tabbedview_view-overview')

        self.assertEquals(
            ['Action 2'],
            browser.css('ul.webactions_buttons a').text)

    @browsing
    def test_webactions_are_html_escaped(self, browser):
        self.login(self.regular_user, browser)

        storage = get_storage()
        storage.update(1, {"title": u"<bold>Action with HTML</bold>"})

        browser.open(self.task, view='tabbedview_view-overview')

        self.assertIn('&lt;bold&gt;Action with HTML&lt;/bold&gt;',
                      browser.css('ul.webactions_buttons a').first.innerHTML)
