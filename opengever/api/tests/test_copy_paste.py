from collective.taskqueue.interfaces import ITaskQueue
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.locking.lock import MEETING_EXCERPT_LOCK
from opengever.testing import assets
from opengever.testing import IntegrationTestCase
from plone.locking.interfaces import ILockable
from plone.namedfile.file import NamedBlobFile
from zope.component import getUtility
import json


class TestCopyPasteAPI(IntegrationTestCase):

    features = ("bumblebee", "doc-properties")

    @browsing
    def test_copy_renames_id(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'source': self.subdossier.absolute_url(),
        }

        browser.open(
            self.leaf_repofolder.absolute_url() + '/@copy',
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers,
        )

        target_id = browser.json[0][u'target'].split('/')[-1]
        self.assertNotEqual(target_id, 'copy_of_' + self.subdossier.id)

        target = self.leaf_repofolder[target_id]
        self.assertEqual(
            set(target.objectIds()) & set(self.subdossier.objectIds()), set())

    @browsing
    def test_copy_renames_title_if_copied_to_same_container(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'source': self.document.absolute_url(),
        }

        with self.observe_children(self.dossier) as children:
            browser.open(
                self.dossier.absolute_url() + '/@copy',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(1, len(children["added"]))
        copy = children["added"].pop()
        self.assertEqual("Copy of " + self.document.title, copy.title)
        self.assertEqual([{u'source': self.document.absolute_url(),
                           u'target': copy.absolute_url()}],
                         browser.json)

    @browsing
    def test_copy_updates_creator(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'source': self.document.absolute_url(),
        }
        browser.open(
            self.dossier.absolute_url() + '/@copy',
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers,
        )

        target_id = browser.json[0][u'target'].split('/')[-1]
        target = self.dossier[target_id]
        self.assertEqual(target.Creator(), self.regular_user.getId())

    @browsing
    def test_copy_paste_checked_out_document_is_forbidden(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'source': self.document.absolute_url(),
        }

        self.checkout_document(self.document)

        with browser.expect_http_error(500):
            browser.open(
                self.empty_dossier.absolute_url() + '/@copy',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertDictEqual(
            {u'message': u'error_checked_out_cannot_be_copied',
             u'translated_message': u'Checked out documents cannot be copied.',
             u'additional_metadata': {},
             u'type': u'CopyError'},
            browser.json)

    @browsing
    def test_can_copy_paste_meeting_excerpt_document(self, browser):
        self.login(self.meeting_user, browser)
        excerpt = self.decided_proposal.load_model().resolve_excerpt_document()
        self.assertTrue(ILockable(excerpt).locked())
        self.assertEqual(MEETING_EXCERPT_LOCK.__name__,
                         ILockable(excerpt).lock_info()[0]['type'].__name__)

        payload = {
            u'source': excerpt.absolute_url(),
        }
        browser.open(
            self.dossier.absolute_url() + '/@copy',
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers,
        )

        target_id = browser.json[0][u'target'].split('/')[-1]
        target = self.dossier[target_id]

        self.assertFalse(ILockable(target).locked())
        self.assertEqual(u"Copy of {}".format(excerpt.title), target.title)

    @browsing
    def test_can_copy_paste_dossier_containing_meeting_excerpt_document(self, browser):
        self.login(self.regular_user, browser)
        # we lock the subsubdocument, simulating a locked meeting excerpt
        ILockable(self.subsubdocument).lock(MEETING_EXCERPT_LOCK)
        self.assertTrue(ILockable(self.subsubdocument).locked())
        self.assertEqual(
            MEETING_EXCERPT_LOCK.__name__,
            ILockable(self.subsubdocument).lock_info()[0]['type'].__name__)

        payload = {
            u'source': self.subsubdossier.absolute_url(),
        }
        browser.open(
            self.empty_dossier.absolute_url() + '/@copy',
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers,
        )
        target_id = browser.json[0][u'target'].split('/')[-1]
        target = self.empty_dossier[target_id]
        copied_doc = target.objectValues()[0]
        self.assertFalse(ILockable(copied_doc).locked())
        self.assertEqual(self.subsubdocument.title, copied_doc.title)

    @browsing
    def test_copying_object_with_read_permissions_is_forbidden(self, browser):
        self.login(self.manager)

        self.subsubdossier.__ac_local_roles_block__ = True
        RoleAssignmentManager(self.subsubdossier).add_or_update_assignment(
            SharingRoleAssignment(self.regular_user.getId(),
                                  ['Reader', 'Contributor'],
                                  self.subsubdossier))

        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=403):
            browser.open(self.empty_dossier, view='/@copy',
                         data=json.dumps({"source": self.subsubdossier.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'copy_object_disallowed',
             u'translated_message': u'You are not allowed to copy this object.',
             u'type': u'Forbidden'},
            browser.json)

        with browser.expect_http_error(code=403):
            browser.open(self.empty_dossier, view='/@copy',
                         data=json.dumps({"source": self.subsubdocument.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'copy_object_disallowed',
             u'translated_message': u'You are not allowed to copy this object.',
             u'type': u'Forbidden'},
            browser.json)

    @browsing
    def test_copy_document_when_not_all_path_elements_are_accessible(self, browser):
        self.login(self.administrator, browser=browser)
        subdossier = create(Builder('dossier')
                            .titled(u'Sub')
                            .within(self.protected_dossier))
        RoleAssignmentManager(subdossier).add_or_update_assignments(
            [SharingRoleAssignment(self.regular_user.id, ['Editor'])])
        doc = create(Builder('document')
                     .titled(u'doc')
                     .within(subdossier))

        self.login(self.regular_user, browser=browser)

        with self.observe_children(self.dossier) as children:
            browser.open(
                '{}/@copy'.format(self.dossier.absolute_url()),
                method='POST',
                data=json.dumps(
                    {'source': u'/'.join(doc.getPhysicalPath()).replace(u'/plone', u'')}
                ),
                headers=self.api_headers)

        self.assertEquals(1, len(children['added']))
        copy = children["added"].pop()

        self.assertEquals(200, browser.status_code)
        self.assertEquals(
            [{u'source': doc.absolute_url(), u'target': copy.absolute_url()}],
            browser.json)

    @browsing
    def test_stores_document_in_bumblebee(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'source': self.subsubdossier.absolute_url(),
        }

        self.subsubdocument.file = NamedBlobFile(
            assets.load('with_gever_properties.docx'),
            filename=unicode('with_gever_properties.docx'))

        with self.observe_children(self.leaf_repofolder) as children:
            browser.open(
                self.leaf_repofolder.absolute_url() + '/@copy',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers,
            )
        dossier = children["added"].pop()
        doc = dossier.values()[0]
        queue = getUtility(ITaskQueue, 'test-queue')
        self.assertIn(doc.absolute_url_path() + "/bumblebee_trigger_storing",
                      (job['url'] for job in queue.queue))
