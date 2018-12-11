from ftw.testbrowser import browsing
from opengever.base.security import elevated_privileges
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
from opengever.ogds.base.actor import ActorLookup
from opengever.testing import IntegrationTestCase
from plone import api
from zope.i18n import translate


class TestHistoryEntries(IntegrationTestCase):

    @property
    def current_user_link(self):
        userid = api.user.get_current().getId()
        actor = ActorLookup(userid).lookup()
        return actor.get_link()

    def test_add_history_entry_when_created_a_disposition(self):
        self.login(self.records_manager)

        entry = IHistoryStorage(self.disposition).get_history()[0]

        self.assertTrue(isinstance(entry, Added))
        self.assertEquals('add', entry.css_class)
        self.assertEquals(u'Added by {}'.format(self.current_user_link),
                          translate(entry.msg(), context=self.request))

    @browsing
    def test_add_history_entry_when_editing_a_disposition(self, browser):
        self.login(self.records_manager, browser)
        browser.open(self.disposition, view='edit')
        browser.fill({'Dossiers': [self.expired_dossier,
                                   self.offered_dossier_to_archive,
                                   self.offered_dossier_to_destroy]})
        browser.find('Save').click()

        entry = IHistoryStorage(self.disposition).get_history()[0]

        self.assertTrue(isinstance(entry, Edited))
        self.assertEquals('edit', entry.css_class)
        self.assertEquals(u'Edited by {}'.format(self.current_user_link),
                          translate(entry.msg(), context=self.request))

    def test_add_history_entry_when_finalize_appraisal_a_disposition(self):
        self.login(self.archivist)
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')

        entry = IHistoryStorage(self.disposition).get_history()[0]

        self.assertTrue(isinstance(entry, Appraised))
        self.assertEquals('appraise', entry.css_class)
        self.assertEquals(u'Appraisal finalized by {}'.format(self.current_user_link),
                          translate(entry.msg(), context=self.request))

    def test_add_history_entry_when_dispose_a_disposition(self):
        self.login(self.records_manager)
        with elevated_privileges():
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-appraise')
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-dispose')

        entry = IHistoryStorage(self.disposition).get_history()[0]

        self.assertTrue(isinstance(entry, Disposed))
        self.assertEquals('dispose', entry.css_class)
        self.assertEquals(
            u'Disposition disposed for the archive by {}'.format(self.current_user_link),
            translate(entry.msg(), context=self.request))

    def test_add_history_entry_when_directly_close_a_disposition(self):
        self.login(self.records_manager)
        IAppraisal(self.disposition).update(dossier=self.offered_dossier_to_archive,
                                            archive=False)
        with elevated_privileges():
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-appraise')
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-appraised-to-closed')

        entry = IHistoryStorage(self.disposition).get_history()[0]

        self.assertTrue(isinstance(entry, AppraisedToClosed))
        self.assertEquals('close', entry.css_class)
        self.assertEquals(
            u'Disposition closed and all dossiers destroyed by {}'.format(
                self.current_user_link),
            translate(entry.msg(), context=self.request))

    def test_add_history_entry_when_archive_a_disposition(self):
        self.login(self.records_manager)
        with elevated_privileges():
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
            u'The archiving confirmed by {}'.format(self.current_user_link),
            translate(entry.msg(), context=self.request))

    def test_add_history_entry_when_close_a_disposition(self):
        self.login(self.records_manager)
        with elevated_privileges():
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
                self.current_user_link),
            translate(entry.msg(), context=self.request))

    def test_add_history_entry_when_refuse_a_disposition(self):
        self.login(self.archivist)
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-refuse')

        entry = IHistoryStorage(self.disposition).get_history()[0]

        self.assertTrue(isinstance(entry, Refused))
        self.assertEquals('refuse', entry.css_class)
        self.assertEquals(
            u'Disposition refused by {}'.format(self.current_user_link),
            translate(entry.msg(), context=self.request))

    def test_ignores_modified_events_during_dossier_destruction(self):
        self.login(self.records_manager)
        with elevated_privileges():
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-appraise')
            IAppraisal(self.disposition).update(dossier=self.offered_dossier_to_destroy,
                                                archive=True)
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-dispose')
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-archive')
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-close')

        self.assertEquals(
            ['disposition-transition-close', 'disposition-transition-archive',
             'disposition-transition-dispose', 'disposition-transition-appraise',
             'added'],
            [item.transition for item in IHistoryStorage(self.disposition).get_history()]
        )


class TestHistoryListingInOverview(IntegrationTestCase):

    @property
    def records_manager_label(self):
        userid = self.records_manager.getId()
        actor = ActorLookup(userid).lookup()
        return actor.get_label()

    @property
    def archivist_label(self):
        userid = self.archivist.getId()
        actor = ActorLookup(userid).lookup()
        return actor.get_label()

    @browsing
    def test_is_sorted_chronological(self, browser):
        self.login(self.archivist, browser)

        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')

        browser.open(self.disposition, view='overview')

        self.assertEquals(
            [u'Appraisal finalized by {}'.format(self.archivist_label),
             u'Added by {}'.format(self.records_manager_label)],
            browser.css('.progress .answer h3').text)

    @browsing
    def test_details_list_dossier_snapshot(self, browser):
        self.login(self.archivist, browser)

        IAppraisal(self.disposition).update(
            dossier=self.offered_dossier_to_archive, archive=False)

        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')

        browser.open(self.disposition, view='overview')

        appraise = browser.css('div.details ul')[0]
        add = browser.css('div.details ul')[1]

        self.assertEquals(
            ["Client1 1.1 / 11 Hannah Baufrau Don't archive",
             "Client1 1.1 / 12 Hans Baumann Don't archive"],
            appraise.css('li').text)

        self.assertEquals(
            ['Client1 1.1 / 11 Hannah Baufrau Archive',
             "Client1 1.1 / 12 Hans Baumann Don't archive"],
            add.css('li').text)

    @browsing
    def test_is_marked_with_corresponding_css_class(self, browser):
        self.login(self.archivist, browser)

        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')

        browser.open(self.disposition, view='overview')

        self.assertEquals('answer appraise',
                          browser.css('.progress .answer')[0].get('class'))
        self.assertEquals('answer add',
                          browser.css('.progress .answer')[1].get('class'))
