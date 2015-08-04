from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.testing import FunctionalTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName


class TestMoveItems(FunctionalTestCase):

    def setUp(self):
        super(TestMoveItems, self).setUp()
        self.request = self.layer['request']

        self.source_repo = create(Builder("repository"))
        self.source_dossier = create(Builder("dossier")
                                     .within(self.source_repo))

    def test_cant_move_items_to_invalid_target(self):
        bad_target = create(Builder("repository"))
        task1 = create(Builder("task")
                       .within(self.source_dossier).titled("a Task"))

        self.assert_contains(self.source_dossier, ['a Task'])
        self.assert_contains(bad_target, [])

        self.move_items([task1], source=self.source_dossier, target=bad_target)

        self.assert_contains(self.source_dossier, ['a Task'])
        self.assert_contains(bad_target, [])

    def test_render_documents_tab_when_no_items_are_selected(self):
        view = self.source_dossier.restrictedTraverse('move_items')

        self.assertEquals("%s#documents" % self.source_dossier.absolute_url(), view())

    def test_render_orig_template_when_no_items_are_selected(self):
        view = self.source_dossier.restrictedTraverse('move_items')
        self.request.form['orig_template'] = "%s#dossiers" % self.source_dossier.absolute_url()
        self.assertEquals("%s#dossiers" % self.source_dossier.absolute_url(), view())

    def test_move_items_to_valid_target(self):
        """ Test integration of move_items method
        """

        target_repo = create(Builder("repository"))

        target_dossier = create(Builder("dossier").within(target_repo))

        doc1 = create(Builder("document")
                      .within(self.source_dossier).titled(u"Dossier \xb6c1"))
        subdossier1 = create(Builder("dossier")
                             .within(self.source_dossier).titled(u"a Dossier"))

        self.assert_contains(self.source_dossier,
                             ['Dossier \xc2\xb6c1', 'a Dossier'])
        self.assert_contains(target_dossier, [])

        self.move_items([doc1, subdossier1],
                        source=self.source_dossier,
                        target=target_dossier)

        self.assert_contains(self.source_dossier, [])
        self.assert_contains(target_dossier,
                             ['Dossier \xc2\xb6c1', 'a Dossier'])

    def test_closed_items_hidden_in_destination_widget(self):
        setRoles(self.portal, TEST_USER_ID, ['Reviewer', 'Manager'])
        target_repo = create(Builder("repository"))

        create(Builder("dossier")
               .within(target_repo)
               .in_state('dossier-state-resolved'))

        self.request['paths'] = '/'.join(self.source_dossier.getPhysicalPath())

        uids = self.get_uids_from_tree_widget()

        self.assertEquals([IUUID(self.source_dossier),
                           IUUID(self.source_repo),
                           IUUID(target_repo)],
                          uids,
                          "Closed dossier found as target in move items")

    def test_open_items_appear_in_destination_widget(self):
        target_repo = create(Builder("repository"))

        target_dossier = create(Builder("dossier").within(target_repo))
        self.request['paths'] = '/'.join(self.source_dossier.getPhysicalPath())

        uids = self.get_uids_from_tree_widget()

        self.assertIn(IUUID(target_dossier),
                      uids,
                      "Active dossier not found as target in move items")

    def get_uids_from_tree_widget(self):
        view = self.source_repo.restrictedTraverse('move_items')
        form = view.form(self.source_repo, self.request)
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
        self.assertEquals(items,
                          [a.Title for a in container.getFolderContents()])


class TestMoveItemsWithTestbrowser(FunctionalTestCase):

    def setUp(self):
        super(TestMoveItemsWithTestbrowser, self).setUp()

        self.source_repo = create(Builder("repository"))
        self.source_dossier = create(Builder("dossier")
                                     .within(self.source_repo))
        self.target_dossier = create(Builder("dossier"))

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
        browser.fill({'Destination': target})
        browser.css('#form-buttons-button_submit').first.click()

    @browsing
    def test_redirects_to_context_and_show_statusmessage_when_obj_cant_be_found(self, browser):
        self.move_items(
            browser, src=self.source_dossier,
            obj='/invalid/path', target=self.target_dossier)

        self.assertEqual(self.source_dossier.absolute_url(), browser.url)
        self.assertEqual(
            "The selected objects can't be found, please try it again.",
            error_messages()[0])

    @browsing
    def test_document_inside_a_task_is_not_movable(self, browser):
        task = create(Builder('task')
                      .titled('Task A')
                      .within(self.source_dossier))
        document = create(Builder('document')
                          .titled(u'Doc A').within(task))

        self.move_items(
            browser, src=task,
            obj=document, target=self.target_dossier)

        self.assertIn(document, task.objectValues())
        self.assertNotIn(document, self.target_dossier.objectValues())
        self.assertEqual(
            'Document Doc A is connected to a Task. Please move the Task.',
            error_messages()[0])

    @browsing
    def test_document_inside_closed_dossier_is_not_movable(self, browser):
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved'))
        document = create(Builder('document')
                          .within(dossier))

        self.move_items(
            browser, src=dossier,
            obj=document, target=self.target_dossier)

        self.assertIn(document, dossier.objectValues())
        self.assertNotIn(document, self.target_dossier.objectValues())
        self.assertEqual(
            [u'Failed to copy following objects: Testdokum\xe4nt'],
            error_messages())

    @browsing
    def test_document_inside_inactive_dossier_is_not_movable(self, browser):
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-inactive'))
        document = create(Builder('document')
                          .within(dossier))

        self.move_items(
            browser, src=dossier,
            obj=document, target=self.target_dossier)

        self.assertIn(document, dossier.objectValues())
        self.assertNotIn(document, self.target_dossier.objectValues())
        self.assertEqual(
            [u'Failed to copy following objects: Testdokum\xe4nt'],
            error_messages())

    @browsing
    def test_task_inside_closed_dossier_is_not_movable(self, browser):
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved'))
        task = create(Builder('task')
                      .within(dossier)
                      .titled(u'My task'))

        self.move_items(
            browser, src=dossier,
            task=task, target=self.target_dossier)

        self.assertIn(task, dossier.objectValues())
        self.assertNotIn(task, self.target_dossier.objectValues())
        self.assertEqual(
            [u'Failed to copy following objects: My task'],
            error_messages())

    @browsing
    def test_mail_inside_closed_dossier_is_not_movable(self, browser):
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved'))
        mail = create(Builder('mail')
                      .within(dossier)
                      .titled(u'My mail'))

        self.move_items(
            browser, src=dossier,
            obj=mail, target=self.target_dossier)

        self.assertIn(mail, dossier.objectValues())
        self.assertNotIn(mail, self.target_dossier.objectValues())
        self.assertEqual(
            [u'Failed to copy following objects: My mail'],
            error_messages())

    @browsing
    def test_task_are_handled_correctly(self, browser):
        task = create(Builder('task')
                      .titled(u'Task')
                      .within(self.source_dossier))

        self.move_items(
            browser, src=self.source_dossier,
            task=task, target=self.target_dossier)

        self.assertIn(task, self.target_dossier.objectValues())

    @browsing
    def test_copy_then_move(self, browser):
        subdossier = create(Builder('dossier').within(self.source_dossier))
        document = create(Builder('document').within(self.source_dossier))

        browser.login()

        # Copy the document
        paths = ['/'.join(document.getPhysicalPath())]
        browser.open(
            self.source_dossier, {'paths:list': paths}, view='copy_items')

        # Move the same document we copied before
        browser.open(
            self.source_dossier, {'paths:list': paths}, view='move_items')
        browser.fill({'Destination': subdossier})

        # Should not cause our check in is_pasting_allowed view to fail
        browser.css('#form-buttons-button_submit').first.click()
