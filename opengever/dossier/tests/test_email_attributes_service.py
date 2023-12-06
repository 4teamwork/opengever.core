from ftw.mail.interfaces import IEmailAddress
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api
from zope.globalrequest import getRequest


class TestEmailAttributesService(IntegrationTestCase):

    @browsing
    def test_service_contains_bcc_if_user_has_modify_portal_content_permission(
            self, browser):
        self.login(self.regular_user, browser)
        self.assertTrue(api.user.has_permission(
            'Modify portal content',
            self.regular_user.getUserName(),
            obj=self.dossier))
        browser.open(self.dossier,
                     view='attributes',
                     headers={'Accept': 'application/json'})
        email = IEmailAddress(getRequest()).get_email_for_object(self.dossier)

        self.assertEquals({u'email': email}, browser.json)

    @browsing
    def test_service_contains_no_bcc_if_dossier_is_resolved(
            self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)
        self.assertFalse(api.user.has_permission(
            'Modify portal content',
            self.regular_user.getUserName(),
            obj=self.dossier))
        browser.open(self.dossier,
                     view='attributes',
                     headers={'Accept': 'application/json'})
        self.assertEquals({}, browser.json)
