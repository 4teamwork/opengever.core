from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import transaction


class TestMoveItems(IntegrationTestCase):

    def test_cant_move_items_to_invalid_target(self):
        self.login(self.manager)
        bad_target = create(Builder("repository"))
        task_title = self.task.title.encode("utf-8")
        self.assert_contains(self.dossier, [task_title])
        self.assert_does_not_contain(bad_target, [task_title])
        self.move_items([self.task], source=self.dossier, target=bad_target)
        self.assert_contains(self.dossier, [task_title])
        self.assert_does_not_contain(bad_target, [task_title])

    def test_render_documents_tab_when_no_items_are_selected(self):
        self.login(self.regular_user)
        view = self.dossier.restrictedTraverse('move_items')
        self.assertEquals("%s#documents" % self.dossier.absolute_url(), view())

    def test_render_orig_template_when_no_items_are_selected(self):
        self.login(self.regular_user)
        view = self.dossier.restrictedTraverse('move_items')
        self.request.form[
            'orig_template'] = "%s#dossiers" % self.dossier.absolute_url()
        self.assertEquals("%s#dossiers" % self.dossier.absolute_url(), view())

    def test_move_items_to_valid_target(self):
        """ Test integration of move_items method
        """
        self.login(self.manager)
        subdossier_title = self.subdossier.title.encode("utf-8")
        doc_title = self.document.title.encode("utf-8")
        self.assert_contains(self.dossier, [doc_title, subdossier_title])
        self.assert_does_not_contain(self.empty_dossier,
                                     [doc_title, subdossier_title])

        self.move_items([self.document, self.subdossier],
                        source=self.dossier,
                        target=self.empty_dossier)

        self.assert_does_not_contain(
            self.dossier, [doc_title, subdossier_title])
        self.assert_contains(self.empty_dossier, [doc_title, subdossier_title])

    def test_only_open_items_appear_in_destination_widget(self):
        self.login(self.dossier_manager)

        self.request['paths'] = '/'.join(self.dossier.getPhysicalPath())

        uids = self.get_uids_from_tree_widget()

        self.assertIn(IUUID(self.empty_dossier), uids,
                      "Active dossier not found as target in move items")

        self.assertNotIn(IUUID(self.archive_dossier), uids,
                         "Closed dossier found as target in move items")

    def get_uids_from_tree_widget(self):
        view = self.branch_repofolder.restrictedTraverse('move_items')
        form = view.form(self.branch_repofolder, self.request)
        form.updateWidgets()

        catalog = getToolByName(self.portal, 'portal_catalog')
        widget = form.widgets['destination_folder']
        query_result = catalog(widget.bound_source.navigation_tree_query)

        return [item.UID for item in query_result]

    def move_items(self, items, source=None, target=None):
        paths = u";;".join(["/".join(i.getPhysicalPath()) for i in items])
        self.request['paths'] = paths
        self.request['form.widgets.request_paths'] = paths
        self.request['form.widgets.destination_folder'] = "/".join(
            target.getPhysicalPath())

        view = source.restrictedTraverse('move_items')
        form = view.form(source, self.request)
        form.updateWidgets()
        form.widgets['destination_folder'].value = target
        form.widgets['request_paths'].value = paths

        form.handle_submit(form, object)

    def assert_contains(self, container, items):
        for item in items:
            self.assertIn(item,
                          [a.Title for a in container.getFolderContents()])

    def assert_does_not_contain(self, container, items):
        for item in items:
            self.assertNotIn(item,
                             [a.Title for a in container.getFolderContents()])


class TestMoveItemsWithTestbrowser(IntegrationTestCase):


    def move_items(self, browser, src, obj=None, task=None, target=None):
        path = None
        task_ids = None

        if isinstance(obj, basestring):
            path = obj
        elif obj is not None:
            path = '/'.join(obj.getPhysicalPath())

        if task:
            task_ids = task.get_sql_object().task_id

        payload = {}
        if task_ids:
            payload['task_ids'] = task_ids
        if path:
            payload['paths:list'] = [path]

        browser.login().open(src, payload, view='move_items')

        if not browser.url.endswith('move_items'):
            # Might have been redirected because of an error
            return

        browser.fill({'Destination': target})
        browser.css('#form-buttons-button_submit').first.click()

    @browsing
    def test_redirects_to_context_and_show_statusmessage_when_obj_cant_be_found(self, browser):
        self.login(self.regular_user)
        self.move_items(
            browser, src=self.dossier,
            obj='/invalid/path', target=self.empty_dossier)

        self.assertEqual(self.dossier.absolute_url(), browser.url)
        self.assertEqual(
            "The selected objects can't be found, please try it again.",
            error_messages()[0])

    @browsing
    def test_document_inside_a_task_is_not_movable(self, browser):
        self.login(self.regular_user)
        self.move_items(
            browser, src=self.task,
            obj=self.taskdocument, target=self.empty_dossier)

        self.assertEqual(
            'Document {} is not movable.'.format(self.taskdocument.title),
            error_messages()[0])
        self.assertIn(self.taskdocument, self.task.objectValues())
        self.assertNotIn(self.taskdocument, self.empty_dossier.objectValues())

    @browsing
    def test_document_inside_closed_dossier_is_not_movable(self, browser):
        self.login(self.dossier_manager)
        self.move_items(
            browser, src=self.archive_dossier,
            obj=self.archive_document, target=self.empty_dossier)

        self.assertEqual(
            ['Can only move objects from open dossiers!'],
            error_messages())
        self.assertIn(self.archive_document,
                      self.archive_dossier.objectValues())
        self.assertNotIn(self.archive_document,
                         self.empty_dossier.objectValues())

    @browsing
    def test_document_inside_inactive_dossier_is_not_movable(self, browser):
        self.login(self.dossier_manager)
        self.move_items(
            browser, src=self.inactive_dossier,
            obj=self.inactive_document, target=self.empty_dossier)

        self.assertEqual(
            ['Can only move objects from open dossiers!'],
            error_messages())
        self.assertIn(self.inactive_document,
                      self.inactive_dossier.objectValues())
        self.assertNotIn(self.inactive_document,
                         self.empty_dossier.objectValues())

    @browsing
    def test_task_inside_closed_dossier_is_not_movable(self, browser):
        self.login(self.dossier_manager)
        self.move_items(
            browser, src=self.archive_dossier,
            task=self.archive_task, target=self.empty_dossier)

        self.assertEqual(
            ['Can only move objects from open dossiers!'],
            error_messages())
        self.assertIn(self.archive_task, self.archive_dossier.objectValues())
        self.assertNotIn(self.archive_task, self.empty_dossier.objectValues())

    @browsing
    def test_mail_inside_closed_dossier_is_not_movable(self, browser):
        self.login(self.dossier_manager)
        self.set_workflow_state('dossier-state-resolved', self.dossier)
        self.move_items(
            browser, src=self.dossier,
            obj=self.mail_eml, target=self.empty_dossier)

        self.assertEqual(
            ['Can only move objects from open dossiers!'],
            error_messages())
        self.assertIn(self.mail_eml, self.dossier.objectValues())
        self.assertNotIn(self.mail_eml, self.empty_dossier.objectValues())

    @browsing
    def test_task_are_handled_correctly(self, browser):
        self.login(self.regular_user)
        task_intid = getUtility(IIntIds).getId(self.subtask)
        self.move_items(
            browser, src=self.task,
            task=self.subtask, target=self.empty_dossier)
        self.subtask = getUtility(IIntIds).getObject(task_intid)
        self.assertIn(self.subtask, self.empty_dossier.objectValues())

    @browsing
    def test_move_items_within_templatefolder_is_possible(self, browser):
        self.login(self.regular_user, browser)
        # if the template folders are not in a valid root, this does not work
        # No idea why it used to work in the functional test?
        templatefolder = create(Builder('templatefolder').within(self.repository_root))
        subtemplatefolder = create(
            Builder('templatefolder').within(templatefolder))
        document = create(Builder('document').within(templatefolder))
        self.move_items(browser, src=templatefolder,
                        obj=document, target=subtemplatefolder)
        self.assertIn(document, subtemplatefolder.objectValues())

    @browsing
    def test_paste_action_not_visible_for_closed_dossiers(self, browser):
        self.login(self.dossier_manager, browser)
        paths = ['/'.join(self.document.getPhysicalPath())]
        browser.open(
            self.dossier, {'paths:list': paths}, view='copy_items')

        browser.open(self.empty_dossier)
        self.assertIsNotNone(
            browser.find('Paste'),
            'Paste should be visible for open dossiers')

        browser.open(self.archive_dossier)
        self.assertIsNone(
            browser.find('Paste'),
            'Paste should not be visible for resolved dossiers')

    @browsing
    def test_copy_then_move(self, browser):
        self.login(self.regular_user, browser)

        # Copy the document
        paths = ['/'.join(self.document.getPhysicalPath())]
        browser.open(
            self.empty_dossier, {'paths:list': paths}, view='copy_items')

        # Move the same document we copied before
        browser.open(
            self.empty_dossier, {'paths:list': paths}, view='move_items')
        browser.fill({'Destination': self.dossier})

        # Should not cause our check in is_pasting_allowed view to fail
        browser.css('#form-buttons-button_submit').first.click()

    @browsing
    def test_reference_number_is_not_reset_when_moving_to_same_parent(self, browser):
        """When a dossier is select to be moved but the target is the current
        parent, the dossier will not actually change the location.
        In this case the reference number should not be changed.
        """
        self.login(self.regular_user, browser)
        browser.open(self.empty_dossier)
        self.assertEquals('Reference Number: Client1 1.1 / 4',
                          browser.css('.reference_number').first.text,
                          'Unexpected reference number. Test fixture changed?')
        dossier_intid = getUtility(IIntIds).getId(self.empty_dossier)

        self.move_items(browser,
                        obj=self.empty_dossier,
                        src=self.leaf_repofolder,
                        target=self.leaf_repofolder)
        assert_no_error_messages()

        #transaction.begin()  # sync
        dossier = getUtility(IIntIds).getObject(dossier_intid)
        browser.open(dossier)
        self.assertEquals('Reference Number: Client1 1.1 / 4',
                          browser.css('.reference_number').first.text,
                          'Moving to the current parent should not change'
                          ' the reference number because the location does'
                          ' not change.')

    @browsing
    def test_reference_number_is_recycled_when_moving_dossier_back(self, browser):
        """When a dossier is moved back to a repository where it was before,
        the original reference number should be recycled.
        """
        self.login(self.regular_user, browser)
        browser.open(self.empty_dossier)
        self.assertEquals('Reference Number: Client1 1.1 / 4',
                          browser.css('.reference_number').first.text,
                          'Unexpected reference number. Test fixture changed?')
        dossier_intid = getUtility(IIntIds).getId(self.empty_dossier)

        # Move to other_repository
        self.move_items(browser,obj=self.empty_dossier,src=self.leaf_repofolder,target=self.empty_repofolder)
        assert_no_error_messages()

        #transaction.begin()  # sync
        dossier = getUtility(IIntIds).getObject(dossier_intid)
        browser.open(dossier)

        self.assertEquals('Reference Number: Client1 2 / 1',
                          browser.css('.reference_number').first.text,
                          'Unexpected reference number after moving.')

        # Move back to source_repo
        self.move_items(browser,
                        obj=dossier,
                        src=self.empty_repofolder,
                        target=self.leaf_repofolder)
        assert_no_error_messages()

        dossier = getUtility(IIntIds).getObject(dossier_intid)
        browser.open(dossier)
        self.assertEquals('Reference Number: Client1 1.1 / 4',
                          browser.css('.reference_number').first.text,
                          'When moving back, the old reference_number should be'
                          ' recycled.')
