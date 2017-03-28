from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.testing import FunctionalTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import json
import transaction


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

    def test_dossier_in_state_resolved_is_not_traversable(self):
        setRoles(self.portal, TEST_USER_ID, ['Reviewer', 'Manager'])
        target_repo = create(Builder("repository"))

        create(Builder("dossier")
               .within(target_repo)
               .in_state('dossier-state-resolved'))

        self.request['start'] = '/'.join(target_repo.getPhysicalPath())
        result = self.get_items_from_widget()
        self.assertEquals(0, len(result['items']), 'Expect no dossier')

    def test_open_items_appear_in_destination_widget(self):
        target_repo = create(Builder("repository"))

        target_dossier = create(Builder("dossier").within(target_repo))
        self.request['paths'] = '/'.join(self.source_dossier.getPhysicalPath())

        self.request['start'] = '/'.join(target_repo.getPhysicalPath())
        result = self.get_items_from_widget()
        self.assertEquals(['/'.join(target_dossier.getPhysicalPath())],
                          [item['path'] for item in result['items']])

    def get_items_from_widget(self):
        widget_name = 'form.widgets.destination_folder'
        path = '@@move_items/++widget++' + widget_name + '/get_reference_data'
        return json.loads(self.source_repo.unrestrictedTraverse(path)())

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

        if not browser.url.endswith('move_items'):
            # Might have been redirected because of an error
            return

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
            'Document Doc A is not movable.',
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
            ['Can only move objects from open dossiers!'],
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
            ['Can only move objects from open dossiers!'],
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
            ['Can only move objects from open dossiers!'],
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
            ['Can only move objects from open dossiers!'],
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
    def test_paste_action_not_visible_for_closed_dossiers(self, browser):
        resolved_dossier = create(Builder('dossier')
                                  .in_state('dossier-state-resolved'))
        document = create(Builder('document').within(self.source_dossier))

        browser.login()
        # Copy the document
        paths = ['/'.join(document.getPhysicalPath())]
        browser.open(
            self.source_dossier, {'paths:list': paths}, view='copy_items')

        browser.open(self.source_dossier)
        self.assertIsNotNone(
            browser.find('Paste'),
            'Paste should be visible for open dossiers')

        browser.open(resolved_dossier)
        self.assertIsNone(
            browser.find('Paste'),
            'Paste should not be visible for resolved dossiers')

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

    @browsing
    def test_reference_number_is_not_reset_when_moving_to_same_parent(self, browser):
        """When a dossier is select to be moved but the target is the current
        parent, the dossier will not actually change the location.
        In this case the reference number should not be changed.
        """
        browser.login().open(self.source_dossier)
        self.assertEquals('Reference Number: Client1 1 / 1',
                          browser.css('.reference_number').first.text,
                          'Unexpected reference number. Test fixture changed?')
        dossier_intid = getUtility(IIntIds).getId(self.source_dossier)

        self.move_items(browser,
                        obj=self.source_dossier,
                        src=self.source_repo,
                        target=self.source_repo)
        assert_no_error_messages()

        transaction.begin()  # sync
        dossier = getUtility(IIntIds).getObject(dossier_intid)
        browser.open(dossier)
        self.assertEquals('Reference Number: Client1 1 / 1',
                          browser.css('.reference_number').first.text,
                          'Moving to the current parent should not change'
                          ' the reference number because the location does'
                          ' not change.')

    @browsing
    def test_reference_number_is_recycled_when_moving_dossier_back(self, browser):
        """When a dossier is moved back to a repository where it was before,
        the original reference number should be recycled.
        """

        browser.login().open(self.source_dossier)
        self.assertEquals('Reference Number: Client1 1 / 1',
                          browser.css('.reference_number').first.text,
                          'Unexpected reference number. Test fixture changed?')
        dossier_intid = getUtility(IIntIds).getId(self.source_dossier)

        # Move to other_repository
        other_repository = create(Builder('repository'))
        self.move_items(browser,
                        obj=self.source_dossier,
                        src=self.source_repo,
                        target=other_repository)
        assert_no_error_messages()

        transaction.begin()  # sync
        dossier = getUtility(IIntIds).getObject(dossier_intid)
        browser.open(dossier)
        self.assertEquals('Reference Number: Client1 2 / 1',
                          browser.css('.reference_number').first.text,
                          'Unexpected reference number after moving.')

        # Move back to source_repo
        self.move_items(browser,
                        obj=dossier,
                        src=other_repository,
                        target=self.source_repo)
        assert_no_error_messages()

        transaction.begin()  # sync
        dossier = getUtility(IIntIds).getObject(dossier_intid)
        browser.open(dossier)
        self.assertEquals('Reference Number: Client1 1 / 1',
                          browser.css('.reference_number').first.text,
                          'When moving back, the old reference_number should be'
                          ' recycled.')
