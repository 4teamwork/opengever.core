from Testing.makerequest import makerequest
from opengever.mail.mail import IOGMailMarker, IOGMail
from opengever.mail.mail import OGMailEditForm
from opengever.mail.testing import OPENGEVER_MAIL_INTEGRATION_TESTING
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from zope.app.component.hooks import setSite
import os
import unittest2 as unittest


class TestOGMailAddition(unittest.TestCase):

    layer = OPENGEVER_MAIL_INTEGRATION_TESTING

    def setUp(self):
        super(TestOGMailAddition, self).setUp()
        self.app = self.layer['app']
        self.portal = self.layer['portal']

        self.portal = makerequest(self.portal)
        setSite(self.portal)
        self.mail_data = open(os.path.join(
                os.path.dirname(__file__),  'mail.txt'), 'r').read()

    def test_title_functionality(self):

        m1 = createContentInContainer(
            self.portal, 'ftw.mail.mail')

        self.portal.get(m1.getId())

        self.failUnless(IOGMailMarker.providedBy(m1))

        self.assertEquals(u'[No Subject]', m1.title)
        self.assertEquals(m1.Title(), '[No Subject]')

        m2 = createContentInContainer(
            self.portal, 'ftw.mail.mail',
            message=NamedBlobFile(self.mail_data, filename=u"mail.eml"))

        #reset title
        self.assertEquals(u'Die B\xfcrgschaft', m2.title)
        self.assertEquals(m2.Title(), 'Die B\xc3\xbcrgschaft')

        IOGMail(m1).title = u'hanspeter'

        self.assertEquals(u'hanspeter', m1.title)
        self.assertEquals(m1.Title(), 'hanspeter')

    def test_editform(self):

        m1 = createContentInContainer(
            self.portal, 'ftw.mail.mail')

        edit_form = OGMailEditForm(m1, self.portal.REQUEST)

        #message field should be in display mode
        self.assertTrue('<span id="form-widgets-message"' in edit_form())
