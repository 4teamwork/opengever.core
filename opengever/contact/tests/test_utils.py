from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.utils import get_contactfolder_url
from opengever.testing import FunctionalTestCase


class TestContactFolderUrl(FunctionalTestCase):

    def test_returns_url_of_the_contactfolder(self):
        contactfolder = create(Builder('contactfolder'))

        self.assertEquals(contactfolder.absolute_url(),
                          get_contactfolder_url())

    def test_none_when_no_contactfolder_exists(self):
        self.assertIsNone(get_contactfolder_url())
