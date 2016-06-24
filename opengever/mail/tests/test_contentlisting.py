from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from plone.app.contentlisting.interfaces import IContentListingObject


class TestMailContentListingObject(FunctionalTestCase):

    def test_mail_is_not_a_document(self):
        mail = create(Builder('mail').with_dummy_message())
        self.assertFalse(IContentListingObject(mail).is_document)
