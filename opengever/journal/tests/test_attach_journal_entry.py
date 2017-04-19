from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.journal.handlers import document_attached_to_email
from opengever.testing import FunctionalTestCase
import transaction


class MockEvent(object):

    def __init__(self, obj):
        self.object = obj


class TestAttachJournalEntry(FunctionalTestCase):

    @browsing
    def test_attaching_document_creates_dossier_level_jounral_entry(self, browser):
        with freeze(datetime(2016, 12, 9, 9, 40)):
            self.dossier = create(Builder('dossier'))
            self.document = create(Builder('document').within(self.dossier))
            document_attached_to_email(self.document, MockEvent(self.document))
            transaction.commit()

        browser.login().open(self.dossier, view=u'tabbedview_view-journal')
        row = browser.css('.listing').first.rows[1]

        self.assertEquals(
            {'Changed by': 'Test User (test_user_1_)',
             'Title': 'Document in dossier attached to email via OfficeConnector',
             'References': u'Documents Testdokum\xe4nt',
             'Comments': '',
             'Time': '09.12.2016 09:40'},
            row.dict())

        self.assertEquals(u'Documents Testdokum\xe4nt',
                          row.dict().get('References'))
        browser.click_on(u'Testdokum\xe4nt')
        self.assertEquals(self.document.absolute_url(), browser.url)
