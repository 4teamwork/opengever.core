from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.ogds.base.actor import Actor
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_NAME


class TestHistoryViewlet(FunctionalTestCase):

    def setUp(self):
        super(TestHistoryViewlet, self).setUp()
        self.user, = create(Builder('fixture').with_user(
            userid=TEST_USER_NAME))
        self.actor = Actor.user(self.user.userid)

    @browsing
    def test_history_viewlet_shows_correct_user_links(self, browser):
        test_doc = create(Builder("document")
                          .attach_file_containing("lorem ipsum",
                                                  name=u"foobar.txt"))
        browser.login().open(test_doc)

        elem = browser.css('#history table.version_history td.actor').first
        self.assertEqual(self.actor.get_link(), elem.normalized_innerHTML)
