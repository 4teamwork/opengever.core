from Products.CMFCore.utils import getToolByName
from datetime import date
from ftw.mail.utils import get_attachments
from opengever.document.interfaces import IDocumentSettings
from opengever.testing import FunctionalTestCase
from opengever.testing import OPENGEVER_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import transaction


MESSAGE_TEXT = 'Mime-Version: 1.0\nContent-Type: multipart/mixed; boundary=908752978\nTo: to@example.org\nFrom: from@example.org\nSubject: Attachment Test\nDate: Thu, 01 Jan 1970 01:00:00 +0100\nMessage-Id: <1>\n\n\n--908752978\nContent-Disposition: attachment;\n	filename*=iso-8859-1\'\'B%FCcher.txt\nContent-Type: text/plain;\n	name="=?iso-8859-1?Q?B=FCcher.txt?="\nContent-Transfer-Encoding: base64\n\nw6TDtsOcCg==\n\n--908752978--\n'

LINEBREAK_MESSAGETEXT = """Mime-Version: 1.0
Content-Type: multipart/mixed; boundary=908752978
To: to@example.org\nFrom: from@example.org
Subject: Attachment Test
Date: Thu, 01 Jan 1970 01:00:00 +0100\nMessage-Id: <1>


--908752978
Content-Disposition: attachment;
	filename=Projekt Test Inputvorschlag.doc
Content-Type: text/plain;
	name="Projekt Test Input
        vorschlag.doc"
Content-Transfer-Encoding: base64

w6TDtsOcCg==

--908752978--
"""


class TestAttachmentExtraction(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestAttachmentExtraction, self).setUp()

        self.grant('Owner','Editor','Contributor', 'Manager')

        self.dossier = createContentInContainer(
            self.portal,
            'opengever.dossier.businesscasedossier',
            title=u'Dossier 1')

        transaction.commit()

    def create_mail(self, data):
        msg = None
        if data:
            msg = NamedBlobFile(
                data=data, contentType=u'message/rfc822',
                filename=u'attachment.txt')

        mail = createContentInContainer(
            self.dossier, 'ftw.mail.mail', message=msg)

        transaction.commit()
        return mail

    def test_extract_attachment(self):
        # adjust default value configuration
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IDocumentSettings)
        proxy.preserved_as_paper_default = False

        mail = self.create_mail(MESSAGE_TEXT)
        self.browser.open(
            '%s/extract_attachments' % mail.absolute_url())

        # not selected any attachment
        self.browser.getControl(name='form.submitted').click()
        self.assertPageContains('You have not selected any attachments')

        self.browser.open(
            '%s/extract_attachments' % mail.absolute_url())
        self.browser.getControl(name='attachments:list').value = [1]
        self.browser.getControl(name='form.submitted').click()

        self.assertPageContains('Created document B\xc3\xbccher')

        # check also the brain and object
        cat = getToolByName(self.portal, 'portal_catalog')
        brain = cat(
            path='/'.join(self.dossier.getPhysicalPath()),
            portal_type="opengever.document.document")[0]

        doc = brain.getObject()

        # check document date
        self.assertEquals(brain.document_date, date.today())
        self.assertEquals(doc.document_date, date.today())

        # check default values
        self.assertFalse(doc.preserved_as_paper)
        self.assertTrue(doc.digitally_available)

    def test_extracting_line_break_mail(self):
        mail = self.create_mail(LINEBREAK_MESSAGETEXT)

        self.browser.open('%s/extract_attachments' % mail.absolute_url())
        self.browser.getControl(name='attachments:list').value = [1]
        self.browser.getControl(name='form.submitted').click()
        docs = self.dossier.listFolderContents(
            {'portal_type': 'opengever.document.document'})
        self.assertTrue(
            'Projekt Test Inputvorschlag' in [dd.Title() for dd in docs])

    def test_deleting_after_extracting(self):
        mail = self.create_mail(MESSAGE_TEXT)

        self.browser.open('%s/extract_attachments' % mail.absolute_url())
        self.browser.getControl(name='attachments:list').value = [1]
        self.browser.getControl(name='delete_action').value = ['all']
        self.browser.getControl(name='form.submitted').click()

        self.assertEquals(
            len(get_attachments(mail.msg)), 0,
            'The attachment deleting after extracting, \
            does not work correctly.')

    def test_extract_attachment_without_docs(self):
        mail = self.create_mail(None)

        self.browser.open(
            '%s/extract_attachments' % mail.absolute_url())
        self.assertCurrentUrl(mail.absolute_url())

    def test_cancel(self):
        mail = self.create_mail(MESSAGE_TEXT)
        self.browser.open(
            '%s/extract_attachments' % mail.absolute_url())

        self.browser.getControl(name='form.cancelled').click()
        self.assertCurrentUrl(mail.absolute_url())
