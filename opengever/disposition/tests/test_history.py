from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.disposition.history import Added
from opengever.disposition.history import Appraised
from opengever.disposition.history import AppraisedToClosed
from opengever.disposition.history import Archived
from opengever.disposition.history import Closed
from opengever.disposition.history import Disposed
from opengever.disposition.history import Edited
from opengever.disposition.history import Refused
from opengever.disposition.interfaces import IAppraisal
from opengever.disposition.interfaces import IHistoryStorage
from opengever.testing import FunctionalTestCase
from plone import api
from zope.i18n import translate
import transaction


class TestHistoryEntries(FunctionalTestCase):

    user_link = '<a href="http://nohost/plone/@@user-details/test_user_1_">'\
                'Test User (test_user_1_)</a>'

    def setUp(self):
        super(TestHistoryEntries, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .as_expired()
                               .having(archival_value=ARCHIVAL_VALUE_WORTHY)
                               .within(self.repository))
        self.dossier2 = create(Builder('dossier')
                               .as_expired()
                               .within(self.repository))

        self.grant('Contributor', 'Editor', 'Reader',
                   'Reviewer', 'Records Manager', 'Archivist')

        self.disposition = create(Builder('disposition')
                             .having(dossiers=[self.dossier1])
                             .within(self.root))

    def test_add_history_entry_when_created_a_disposition(self):
        entry = IHistoryStorage(self.disposition).get_history()[0]

        self.assertTrue(isinstance(entry, Added))
        self.assertEquals('add', entry.css_class)
        self.assertEquals(u'Added by {}'.format(self.user_link),
                          translate(entry.msg(), context=self.request))

    @browsing
    def test_add_history_entry_when_editing_a_disposition(self, browser):
        browser.login().open(self.disposition, view='edit')
        browser.fill({'Dossiers': [self.dossier1, self.dossier2]})
        browser.find('Save').click()

        entry = IHistoryStorage(self.disposition).get_history()[0]

        self.assertTrue(isinstance(entry, Edited))
        self.assertEquals('edit', entry.css_class)
        self.assertEquals(u'Edited by {}'.format(self.user_link),
                          translate(entry.msg(), context=self.request))

    def test_add_history_entry_when_finalize_appraisal_a_disposition(self):
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')

        entry = IHistoryStorage(self.disposition).get_history()[0]

        self.assertTrue(isinstance(entry, Appraised))
        self.assertEquals('appraise', entry.css_class)
        self.assertEquals(u'Appraisal finalized by {}'.format(self.user_link),
                          translate(entry.msg(), context=self.request))

    def test_add_history_entry_when_dispose_a_disposition(self):
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-dispose')

        entry = IHistoryStorage(self.disposition).get_history()[0]

        self.assertTrue(isinstance(entry, Disposed))
        self.assertEquals('dispose', entry.css_class)
        self.assertEquals(
            u'Disposition disposed for the archive by {}'.format(self.user_link),
            translate(entry.msg(), context=self.request))

    def test_add_history_entry_when_directly_close_a_disposition(self):
        IAppraisal(self.disposition).update(dossier=self.dossier1,
                                            archive=False)
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraised-to-closed')

        entry = IHistoryStorage(self.disposition).get_history()[0]

        self.assertTrue(isinstance(entry, AppraisedToClosed))
        self.assertEquals('close', entry.css_class)
        self.assertEquals(
            u'Disposition closed and all dossiers destroyed by {}'.format(
                self.user_link),
            translate(entry.msg(), context=self.request))

    def test_add_history_entry_when_archive_a_disposition(self):
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-dispose')
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-archive')

        entry = IHistoryStorage(self.disposition).get_history()[0]

        self.assertTrue(isinstance(entry, Archived))
        self.assertEquals('archive', entry.css_class)
        self.assertEquals(
            u'The archiving confirmed by {}'.format(self.user_link),
            translate(entry.msg(), context=self.request))

    def test_add_history_entry_when_close_a_disposition(self):
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-dispose')
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-archive')
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-close')

        entry = IHistoryStorage(self.disposition).get_history()[0]

        self.assertTrue(isinstance(entry, Closed))
        self.assertEquals('close', entry.css_class)
        self.assertEquals(
            u'Disposition closed and all dossiers destroyed by {}'.format(
                self.user_link),
            translate(entry.msg(), context=self.request))

    def test_add_history_entry_when_refuse_a_disposition(self):
        self.grant('Archivist')
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-refuse')

        entry = IHistoryStorage(self.disposition).get_history()[0]

        self.assertTrue(isinstance(entry, Refused))
        self.assertEquals('refuse', entry.css_class)
        self.assertEquals(
            u'Disposition refused by {}'.format(self.user_link),
            translate(entry.msg(), context=self.request))

    def test_ignores_modified_events_during_dossier_destruction(self):
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')
        IAppraisal(self.disposition).update(dossier=self.dossier1,
                                            archive=True)
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-dispose')
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-archive')
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-close')

        history = IHistoryStorage(self.disposition).get_history()
        self.assertEquals(
            'disposition-transition-close', history[0].transition)
        self.assertEquals(
            'disposition-transition-archive', history[1].transition)


class TestHistoryListingInOverview(FunctionalTestCase):

    def setUp(self):
        super(TestHistoryListingInOverview, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .as_expired()
                               .having(archival_value=ARCHIVAL_VALUE_WORTHY)
                               .within(self.repository))
        self.dossier2 = create(Builder('dossier')
                               .as_expired()
                               .having(archival_value=ARCHIVAL_VALUE_WORTHY)
                               .within(self.repository))
        self.grant(
            'Contributor', 'Editor', 'Reader', 'Reviewer',
            'Records Manager', 'Archivist')

        self.disposition = create(Builder('disposition')
                             .having(dossiers=[self.dossier1, self.dossier2])
                             .within(self.root))

        IAppraisal(self.disposition).update(
            dossier=self.dossier2, archive=False)

        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')
        transaction.commit()

    @browsing
    def test_is_sorted_chronological(self, browser):
        browser.login().open(self.disposition, view='tabbedview_view-overview')

        self.assertEquals(
            ['Appraisal finalized by Test User (test_user_1_)',
             'Added by Test User (test_user_1_)'],
            browser.css('.progress .answer h3').text)

    @browsing
    def test_details_list_dossier_snapshot(self, browser):
        browser.login().open(self.disposition, view='tabbedview_view-overview')

        appraise = browser.css('div.details ul')[0]
        add = browser.css('div.details ul')[1]

        self.assertEquals(
            ['Client1 1 / 1 Archive', "Client1 1 / 2 Don't archive"],
            appraise.css('li').text)
        self.assertEquals(
            ['Client1 1 / 1 Archive', 'Client1 1 / 2 Archive'],
            add.css('li').text)

    @browsing
    def test_is_marked_with_corresponding_css_class(self, browser):
        browser.login().open(self.disposition, view='tabbedview_view-overview')

        self.assertEquals('answer appraise',
                          browser.css('.progress .answer')[0].get('class'))
        self.assertEquals('answer add',
                          browser.css('.progress .answer')[1].get('class'))
