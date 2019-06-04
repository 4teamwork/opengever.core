from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.interfaces import IEmailAddress
from ftw.mail.interfaces import IMailSettings
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.testing import FunctionalTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds


class TestIntIdEmailAddressAdapter(FunctionalTestCase):

    def setUp(self):
        super(TestIntIdEmailAddressAdapter, self).setUp()

        self.request = self.layer['request']
        alsoProvides(self.request, IOpengeverBaseLayer)

        self.intids = getUtility(IIntIds)

        self.dossier = create(Builder('dossier'))

        self.mail_domain = u'opengever.example.com'
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSettings)
        mail_settings.mail_domain = self.mail_domain

    def test_mail_in_address_for_dossier(self):
        intid = self.intids.queryId(self.dossier)
        expected = "%s@%s" % (intid, self.mail_domain)

        adapter = IEmailAddress(self.request)
        mail_address = adapter.get_email_for_object(self.dossier)
        self.assertEquals(expected, mail_address)

    def test_address_resolves_to_dossier(self):
        intid = self.intids.queryId(self.dossier)
        email_address = "%s@%s" % (intid, self.mail_domain)

        adapter = IEmailAddress(self.request)
        obj = adapter.get_object_for_email(email_address)
        self.assertEquals(self.dossier, obj)
