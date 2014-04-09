from opengever.testing import FunctionalTestCase
from opengever.testing import create_ogds_user
from zExceptions import NotFound


class TestUserDetails(FunctionalTestCase):

    use_browser = True

    def test_user_details(self):
        create_ogds_user('hugo.boss', lastname='Boss', firstname='Hugo',
                         groups=('group_a', 'group_b'))

        self.browser.open('%s/@@user-details/hugo.boss' % self.portal.absolute_url())

        self.assertEquals('Boss Hugo (hugo.boss)',
            self.browser.locate('h1.documentFirstHeading').text)

        self.assertEquals(['group_a', 'group_b'],
            [node.text for node in self.browser.css('.groups a')])

    def test_user_details_return_not_found_for_not_exisiting_user(self):
        with self.assertRaises(NotFound):
            self.browser.open('%s/@@user-details/hugo.boss' % self.portal.absolute_url())
