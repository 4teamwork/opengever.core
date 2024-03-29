from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrashed
from opengever.trash.trash import ITrasher


class TestTrashAPI(IntegrationTestCase):

    def setUp(self):
        super(TestTrashAPI, self).setUp()

    @browsing
    def test_trash_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document.absolute_url() + '/@trash',
                     method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(204, browser.status_code)
        self.assertTrue(ITrashed.providedBy(self.document))

    @browsing
    def test_trash_trashed_document_gives_bad_request(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document.absolute_url() + '/@trash',
                     method='POST', headers={'Accept': 'application/json'})

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.document.absolute_url() + '/@trash',
                         method='POST', headers={'Accept': 'application/json'})

        self.assertEqual(
            browser.json['translated_message'], u'Already trashed')

    @browsing
    def test_trash_checked_out_document_gives_bad_request(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document.absolute_url() + '/@checkout',
                     method='POST', headers={'Accept': 'application/json'})

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.document.absolute_url() + '/@trash',
                         method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(
            browser.json['translated_message'],
            u'Cannot trash a checked-out document')

    @browsing
    def test_trash_excerpt_gives_bad_request(self, browser):
        self.activate_feature('meeting')
        self.login(self.meeting_user, browser)

        excerpt = self.decided_proposal.get_excerpt()

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(excerpt.absolute_url() + '/@trash',
                         method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(
            browser.json['translated_message'],
            u'Cannot trash a document that has been returned as excerpt')

    @browsing
    def test_trashing_non_trashable_object_raises_bad_request(self, browser):
        self.login(self.manager, browser=browser)

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.branch_repofolder.absolute_url() + '/@trash',
                         method='POST', headers={'Accept': 'application/json'})

        self.assertEqual(
            browser.json['translated_message'],
            u'Object is not trashable')

    @browsing
    def test_trash_document_without_permission_gives_401(self, browser):
        self.login(self.regular_user, browser)

        self.document.aq_parent.manage_permission(
            'opengever.trash: Trash content', roles=[], acquire=0)
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(self.document.absolute_url() + '/@trash',
                         method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(
            browser.json[u'message'],
            u'You are not authorized to access this resource.')

    @browsing
    def test_trash_document_template_is_not_allowed(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(self.normal_template, view='/@trash',
                         method='POST', headers={'Accept': 'application/json'})

        self.assertEqual(
            browser.json[u'message'],
            u'You are not authorized to access this resource.')

    @browsing
    def test_untrash_document(self, browser):
        self.login(self.regular_user, browser)
        trasher = ITrasher(self.document)
        trasher.trash()
        browser.open(self.document.absolute_url() + '/@untrash',
                     method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(204, browser.status_code)
        self.assertFalse(ITrashed.providedBy(self.document))

    @browsing
    def test_untrash_document_without_permission_gives_401(self, browser):
        self.login(self.regular_user, browser)

        self.document.aq_parent.manage_permission(
            'opengever.trash: Untrash content', roles=[], acquire=0)
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(self.document.absolute_url() + '/@untrash',
                         method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(
            browser.json[u'message'],
            u'You are not authorized to access this resource.')

    @browsing
    def test_untrashing_non_trashed_object_raises_unathorized(self, browser):
        self.login(self.manager, browser=browser)

        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(self.document.absolute_url() + '/@untrash',
                         method='POST', headers={'Accept': 'application/json'})

    @browsing
    def test_trash_workspace_folder(self, browser):
        self.login(self.workspace_member, browser)

        self.assertFalse(ITrashed.providedBy(self.workspace_folder))
        self.assertFalse(ITrashed.providedBy(self.workspace_folder_document))

        browser.open(self.workspace_folder.absolute_url() + '/@trash',
                     method='POST', headers={'Accept': 'application/json'})
        self.assertEqual(204, browser.status_code)
        self.assertTrue(ITrashed.providedBy(self.workspace_folder))
        self.assertTrue(ITrashed.providedBy(self.workspace_folder_document))
