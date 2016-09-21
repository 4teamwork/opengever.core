from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.interfaces import IReferenceNumber
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from zExceptions import Unauthorized


class TestPrivateFolder(FunctionalTestCase):

    @browsing
    def test_is_addable_on_private_root(self, browser):
        self.grant('Manager')

        root = create(Builder('private_root'))

        browser.login().open(root)
        factoriesmenu.add('Private folder')
        browser.fill({'User ID': u'franz.mueller'})
        browser.click_on('Save')

        self.assertEquals([u'franz.mueller'], browser.css('h1').text)

    @browsing
    def test_is_only_addable_by_manager(self, browser):
        root = create(Builder('private_root'))

        with self.assertRaises(Unauthorized):
            browser.login().open(root, view='++add++opengever.private.folder')
            browser.fill({'User ID': TEST_USER_ID})
            browser.click_on('Save')

    def test_object_id_is_userid(self):
        folder = create(Builder('private_folder').having(userid=TEST_USER_ID))
        self.assertEquals(TEST_USER_ID, folder.getId())

    def test_title_is_corresponding_users_label(self):
        folder = create(Builder('private_folder').having(userid=TEST_USER_ID))
        self.assertEquals('Test User (test_user_1_)', folder.Title())

    def test_uses_userid_as_reference_number_part(self):
        folder = create(Builder('private_folder').having(userid=TEST_USER_ID))

        self.assertEquals('Client1 test_user_1_',
                          IReferenceNumber(folder).get_number())
