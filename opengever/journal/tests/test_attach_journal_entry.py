from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.journal.handlers import document_attached_to_email
from opengever.journal.handlers import dossier_attached_to_email
from opengever.testing import FunctionalTestCase
import transaction


class MockEvent(object):
    """A convenience class to conform to a journal event."""

    def __init__(self, obj, documents=None):
        self.object = obj
        self.documents = documents


class TestAttachJournalEntry(FunctionalTestCase):
    """Test journal entries from OC attach events."""

    @browsing
    def test_attaching_document_creates_dossier_level_jounral_entry(self, browser):  # noqa
        with freeze(datetime(2016, 12, 9, 9, 40)):
            self.dossier = create(Builder('dossier'))
            self.document = create(Builder('document')
                                   .titled(u'docu-1')
                                   .within(self.dossier))
            document_attached_to_email(self.document, MockEvent(self.document))
            dossier_attached_to_email(
                self.dossier, MockEvent(self.dossier, [self.document]))
            transaction.commit()

        browser.login()
        browser.open(self.dossier, view=u'tabbedview_view-journal')
        row = browser.css('.listing').first.rows[1]

        self.assertEquals(
            {'Changed by': 'Test User (test_user_1_)',
             'Title': 'Document in dossier attached to email via '
             'OfficeConnector',
             'References': u'Documents docu-1',
             'Comments': '',
             'Time': '09.12.2016 09:40'},
            row.dict())

        self.assertEquals(u'Documents docu-1',
                          row.dict().get('References'))
        browser.click_on(u'docu-1')
        self.assertEquals(self.document.absolute_url(), browser.url)

        browser.open(self.document, view=u'tabbedview_view-journal')
        row = browser.css('.listing').first.rows[1]

        self.assertEquals(
            {'Changed by': 'Test User (test_user_1_)',
             'Title': 'Document attached to email via OfficeConnector',
             'References': '',
             'Comments': '',
             'Time': '09.12.2016 09:40'},
            row.dict())

        # Second pass with 2 documents in a dossier
        with freeze(datetime(2016, 12, 9, 9, 40)):
            self.document_2 = create(Builder('document')
                                     .titled(u'docu-2')
                                     .within(self.dossier))
            document_attached_to_email(self.document, MockEvent(self.document))
            dossier_attached_to_email(
                self.dossier, MockEvent(self.dossier, [
                    self.document, self.document_2]))
            transaction.commit()

        browser.open(self.dossier, view=u'tabbedview_view-journal')
        row = browser.css('.listing').first.rows[1]

        self.assertEquals(
            {'Changed by': 'Test User (test_user_1_)',
             'Title': 'Document in dossier attached to email via '
             'OfficeConnector',
             'References': u'Documents docu-1 docu-2',
             'Comments': '',
             'Time': '09.12.2016 09:40'},
            row.dict())

        self.assertEquals(u'Documents docu-1 docu-2',
                          row.dict().get('References'))
        browser.click_on(u'docu-1')
        self.assertEquals(self.document.absolute_url(), browser.url)

        browser.open(self.dossier, view=u'tabbedview_view-journal')
        browser.click_on(u'docu-2')
        self.assertEquals(self.document_2.absolute_url(), browser.url)

        browser.open(self.document, view=u'tabbedview_view-journal')
        row = browser.css('.listing').first.rows[1]

        self.assertEquals(
            {'Changed by': 'Test User (test_user_1_)',
             'Title': 'Document attached to email via OfficeConnector',
             'References': '',
             'Comments': '',
             'Time': '09.12.2016 09:40'},
            row.dict())
