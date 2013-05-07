from Products.CMFCore.utils import getToolByName
from datetime import date
from ftw.mail.utils import get_attachments
from opengever.document.interfaces import IDocumentSettings
from opengever.testing import OPENGEVER_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import login, setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from zope.component import getUtility
from zope.schema import getFields
import transaction
import unittest2 as unittest


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


class TestAttachmentExtraction(unittest.TestCase):

    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestAttachmentExtraction, self).setUp()
        self.app = self.layer.get('app')
        self.portal = self.layer.get('portal')

        setRoles(self.portal, TEST_USER_ID, ['Member', 'Contributor', 'Editor'])
        login(self.portal, TEST_USER_NAME)

        # create some content
        fti = getUtility(IDexterityFTI, name='ftw.mail.mail')
        schema = fti.lookupSchema()
        field_type = getFields(schema)['message']._type

        self.dossier = createContentInContainer(
            self.portal,
            'opengever.dossier.businesscasedossier',
            title=u'Dossier 1')

        self.mail1 = createContentInContainer(
            self.dossier, 'ftw.mail.mail',
            message=field_type(data=MESSAGE_TEXT,
                               contentType=u'message/rfc822',
                               filename=u'attachment.txt'))

        self.mail2 = createContentInContainer(self.dossier, 'ftw.mail.mail', title=u'Mail 1')

        self.mail3 = createContentInContainer(
            self.dossier, 'ftw.mail.mail',
            message=field_type(data=LINEBREAK_MESSAGETEXT,
                               contentType=u'message/rfc822',
                               filename=u'attachment.txt'))

        transaction.commit()

        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        setRoles(self.portal, TEST_USER_ID, ['Owner','Editor','Contributor', 'Manager'])
        self.browser.addHeader(
            'Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IDocumentSettings)
        proxy.preserved_as_paper_default = False

        transaction.commit()

    def test_extract_attachment(self):
        self.browser.open(
            '%s/extract_attachments' % self.mail1.absolute_url())

        # not selected any attachment
        self.browser.getControl(name='form.submitted').click()
        self.assertTrue(
            'You have not selected any attachments' in self.browser.contents)

        self.browser.open(
            '%s/extract_attachments' % self.mail1.absolute_url())
        self.browser.getControl(name='attachments:list').value=[1]
        self.browser.getControl(name='form.submitted').click()

        self.assertTrue('Created document B\xc3\xbccher' in self.browser.contents)

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

    def test_extracting_line_break_mail(self):

        self.browser.open('%s/extract_attachments' % self.mail3.absolute_url())
        self.browser.getControl(name='attachments:list').value=[1]
        self.browser.getControl(name='form.submitted').click()
        docs = self.dossier.listFolderContents(
            {'portal_type':'opengever.document.document'})
        self.assertTrue(
            'Projekt Test Inputvorschlag' in [dd.Title() for dd in docs])

    def test_deleting_after_extracting(self):
        self.browser.open('%s/extract_attachments' % self.mail1.absolute_url())
        self.browser.getControl(name='attachments:list').value=[1]
        self.browser.getControl(name='delete_action').value=['all']
        self.browser.getControl(name='form.submitted').click()

        self.assertEquals(len(get_attachments(self.mail1.msg)), 0)

    def test_extract_attachment_without_docs(self):
        self.browser.open(
            '%s/extract_attachments' % self.mail2.absolute_url())
        self.assertEquals(self.browser.url, self.mail2.absolute_url())

    def test_cancel(self):
        self.browser.open(
            '%s/extract_attachments' % self.mail1.absolute_url())
        self.browser.getControl(name='form.cancelled').click()
        self.assertEquals(self.browser.url, self.mail1.absolute_url())
