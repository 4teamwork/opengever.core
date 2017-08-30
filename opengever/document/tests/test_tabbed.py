from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from plone.locking.interfaces import IRefreshableLockable


class TestDocumentQuickupload(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentQuickupload, self).setUp()
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_upload_box_is_hidden_when_document_is_not_checked_out(self, browser):
        document = create(Builder('document').within(self.dossier))

        browser.login().open(document)
        self.assertEquals([], browser.css('#uploadbox'),
                          'uploadbox is wrongly displayed')

    @browsing
    def test_upload_box_is_hidden_when_document_is_locked(self, browser):
        document = create(Builder('document').within(self.dossier))
        IRefreshableLockable(document).lock()

        browser.login().open(document)
        self.assertEquals([], browser.css('#uploadbox'),
                          'uploadbox is wrongly displayed')

    @browsing
    def test_upload_box_is_shown_when_document_is_checked_out_and_not_locked(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .checked_out())

        browser.login().open(document)
        self.assertNotEquals(0, len(browser.css('#uploadbox')),
                             'Uploadbox is not displayed, but should.')

    @browsing
    def test_upload_box_is_also_shown_in_a_resolved_task(self, browser):
        create(Builder('ogds_user').id(u'hugo.boss'))
        task = create(Builder('task')
                      .having(responsible='hugo.boss', issuer='hugo.boss')
                      .within(self.dossier)
                      .in_state('task-state-tested-and-closed'))
        document = create(Builder('document')
                          .within(task)
                          .checked_out())

        self.grant('Reader')
        self.dossier.manage_setLocalRoles(
            TEST_USER_ID, ['Reader', 'Contributor', 'Editor'])
        self.dossier.reindexObjectSecurity()

        browser.login().open(document)
        self.assertNotEquals(0, len(browser.css('#uploadbox')),
                             'Uploadbox is not displayed, but should.')
