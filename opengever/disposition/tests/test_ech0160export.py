from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import FunctionalTestCase


class TesteCH0160Deployment(FunctionalTestCase):

    def setUp(self):
        super(TesteCH0160Deployment, self).setUp()
        self.root = create(Builder('repository_root')
                           .having(title_de=u'Ordnungssytem 2000'))
        self.folder = create(Builder('repository').within(self.root))

    @browsing
    def test_returns_zip_file_stream(self, browser):
        dossier_a = create(Builder('dossier').within(self.folder))
        create(Builder('document').with_dummy_content().within(dossier_a))

        with freeze(datetime(2016, 6, 11)):
            view = self.portal.unrestrictedTraverse('ech0160_export')
            view()

            self.assertEquals(
                'application/zip',
                self.request.response.headers.get('content-type'))
            self.assertEquals(
                'inline; filename="SIP_20160611_PLONE_MyRef.zip"',
                self.request.response.headers.get('content-disposition'))
