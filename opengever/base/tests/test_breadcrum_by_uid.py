from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from plone.uuid.interfaces import IUUID


class TestBreadcrumbByUidView(FunctionalTestCase):

    def setUp(self):
        super(TestBreadcrumbByUidView, self).setUp()

        self.root = create(Builder('repository_root').titled(u'Repository'))
        self.repo = create(Builder('repository')
                           .within(self.root)
                           .titled(u'Testposition'))
        self.dossier = create(Builder('dossier')
                              .within(self.repo)
                              .titled(u'Dossier 1'))

        self.view = self.portal.restrictedTraverse('breadcrumb_by_uid')

    def test_resolve_dossier(self):
        self.portal.REQUEST['ploneuid'] = IUUID(self.dossier)
        view = self.portal.restrictedTraverse('breadcrumb_by_uid')
        self.assertEquals('Repository > 1. Testposition > Dossier 1', view())

    def test_raise_attributerror_if_no_uid_is_provided(self):
        with self.assertRaises(AttributeError):
            self.portal.restrictedTraverse('breadcrumb_by_uid')()

    def test_raise_attributerror_if_uid_is_unkown(self):
        self.portal.REQUEST['ploneuid'] = 'doesnotexists'
        view = self.portal.restrictedTraverse('breadcrumb_by_uid')
        with self.assertRaises(AttributeError):
            view()
