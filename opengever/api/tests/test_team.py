from ftw.testbrowser import browsing
from opengever.ogds.models.team import Team
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest


class TestTeamGet(IntegrationTestCase):

    def setUp(self):
        super(TestTeamGet, self).setUp()
        self.team_id = Team.get_one(groupid='projekt_a').team_id

    @browsing
    def test_user_default_response(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.contactfolder,
                     view='@team/{}'.format(self.team_id),
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/kontakte/@team/{}'.format(
                self.team_id),
             u'@type': u'virtual.ogds.team'},
            browser.json)

    @browsing
    def test_raises_bad_request_when_userid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.contactfolder,
                         view='@team',
                         headers=self.api_headers)

    @browsing
    def test_raises_bad_request_when_too_many_params_are_given(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.contactfolder,
                         view='@team/{}/foobar'.format(self.team_id),
                         headers=self.api_headers)
