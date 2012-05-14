from opengever.mail.mail import IOGMailMarker, IOGMail
from opengever.mail.mail import OGMailEditForm, OGMailBase
from opengever.mail.testing import OPENGEVER_MAIL_INTEGRATION_TESTING
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
import os
import unittest2 as unittest


class TestOGMailAddition(unittest.TestCase):

    layer = OPENGEVER_MAIL_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

        self.mail_data = open(os.path.join(
                os.path.dirname(__file__),  'mail.txt'), 'r').read()

    def test_title_functionality(self):
        m1 = createContentInContainer(
            self.portal, 'ftw.mail.mail')

        self.failUnless(IOGMailMarker.providedBy(m1))

        #reset title
        setattr(OGMailBase(m1), 'title', u'')
        self.assertEquals(u'[No Subject]', m1.title)

        m1.message = NamedBlobFile(self.mail_data, filename=u"mail.eml")
        #reset title
        setattr(OGMailBase(m1), 'title', u'')
        self.assertEquals(u'Die B\xfcrgschaft', m1.title)

        IOGMail(m1).title = u'hanspeter'
        self.assertEquals(u'hanspeter', m1.title)

    def test_editform(self):
        m1 = createContentInContainer(
            self.portal, 'ftw.mail.mail')

        edit_form = OGMailEditForm(m1, self.portal.REQUEST)

        #message field should be in display mode
        self.assertTrue('<span id="form-widgets-message"' in edit_form())
