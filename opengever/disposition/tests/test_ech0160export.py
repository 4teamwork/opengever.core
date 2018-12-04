from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase


class TesteCH0160Deployment(IntegrationTestCase):

    @browsing
    def test_returns_zip_file_stream(self, browser):
        self.login(self.records_manager)

        self.disposition.transfer_number = "10xy"

        with freeze(datetime(2016, 6, 11)):
            view = self.disposition.unrestrictedTraverse('ech0160_export')
            view()

            self.assertEquals(
                'application/zip',
                self.request.response.headers.get('content-type'))
            self.assertEquals(
                'inline; filename="SIP_20160611_PLONE_10xy.zip"',
                self.request.response.headers.get('content-disposition'))
