from ftw.builder import Builder
from ftw.builder import create
from opengever.quota.interfaces import IQuotaSubject
from opengever.quota.primary import IPrimaryBlobFieldQuota
from opengever.testing import FunctionalTestCase


class TestPrimaryFieldQuotaSubject(FunctionalTestCase):

    def test_get_size_on_document(self):
        # XXX remove me when quota support is enabled on documents
        self.portal.portal_types['opengever.document.document'].behaviors += (
            IPrimaryBlobFieldQuota.__identifier__,
        )
        document = create(Builder('document')
                          .attach_file_containing('Hello World'))
        self.assertEquals(11, IQuotaSubject(document).get_size())

    def test_get_size_on_mails(self):
        # XXX remove me when quota support is enabled on mails
        self.portal.portal_types['ftw.mail.mail'].behaviors += (
            IPrimaryBlobFieldQuota.__identifier__,
        )
        document = create(Builder('mail')
                          .with_message('Not really an email'))
        self.assertEquals(19, IQuotaSubject(document).get_size())
