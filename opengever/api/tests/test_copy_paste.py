from collective.taskqueue.interfaces import ITaskQueue
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.testing import assets
from opengever.testing import IntegrationTestCase
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
    def test_copy_document_when_not_all_path_elemnts_are_accessible(self, browser):
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
