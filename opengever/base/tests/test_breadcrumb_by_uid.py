from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID


class TestBreadcrumbByUIDView(IntegrationTestCase):


    def test_resolve_dossier(self):
        self.login(self.regular_user)

        self.portal.REQUEST['ploneuid'] = IUUID(self.dossier)

        view = self.portal.restrictedTraverse('breadcrumb_by_uid')
        self.assertEquals(
            'Ordnungssystem > 1. F\xc3\xbchrung > 1.1. Vertr\xc3\xa4ge '
            'und Vereinbarungen > Vertr\xc3\xa4ge mit der kantonalen '
            'Finanzverwaltung',
            view())

    def test_raise_attributerror_if_no_uid_is_provided(self):
        self.login(self.regular_user)

        with self.assertRaises(AttributeError):
            self.portal.restrictedTraverse('breadcrumb_by_uid')()

    def test_raise_attributerror_if_uid_is_unkown(self):
        self.login(self.regular_user)

        self.portal.REQUEST['ploneuid'] = 'doesnotexists'
        view = self.portal.restrictedTraverse('breadcrumb_by_uid')
        with self.assertRaises(AttributeError):
            view()
