from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
import os


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


class TestECH0160StoreView(IntegrationTestCase):

    @browsing
    def test_generates_sip_package_and_stores_it_as_a_blob_on_the_filesystem(self, browser):
        self.login(self.records_manager, browser=browser)

        self.set_workflow_state('disposition-state-disposed', self.disposition)
        self.disposition.transfer_number = "10xy"
        self.assertFalse(self.disposition.has_sip_package())

        with freeze(datetime(2016, 6, 11)):
            browser.open(self.disposition, view='ech0160_store')

        self.assertEquals(
            ['SIP Package generated successfully.'], info_messages())
        self.assertTrue(self.disposition.has_sip_package())


class TestECH0160DownloadView(IntegrationTestCase):

    @browsing
    def test_shows_status_message_when_no_zip_is_stored(self, browser):
        self.login(self.archivist, browser=browser)

        self.set_workflow_state('disposition-state-disposed', self.disposition)
        browser.open(self.disposition, view='ech0160_download')
        self.assertEquals([u'No SIP Package generated for this disposition.'],
                          error_messages())

    @browsing
    def test_streams_zip_when_sip_package_is_stored(self, browser):
        self.login(self.archivist, browser=browser)

        self.set_workflow_state('disposition-state-disposed', self.disposition)
        self.disposition.transfer_number = "10xy"
        self.disposition.store_sip_package()

        with freeze(datetime(2016, 6, 11)):
            browser.open(self.disposition, view='ech0160_download')

        self.assertEquals(
            'application/zip', browser.headers.get('content-type'))
        self.assertEquals(
            "attachment; filename*=UTF-8''SIP_20160611_PLONE_10xy.zip",
            browser.headers.get('content-disposition'))
