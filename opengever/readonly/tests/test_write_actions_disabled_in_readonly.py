from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import IntegrationTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode


class TestAddActionsDisabledInReadOnly(IntegrationTestCase):

    def assert_no_factories_menu(self, browser, context):
        with ZODBStorageInReadonlyMode():
            browser.open(context)
            with self.assertRaises(ValueError) as cm:
                factoriesmenu.addable_types()

        self.assertEquals('Factories menu is not visible.', str(cm.exception))

    @browsing
    def test_no_addable_types_in_repofolder(self, browser):
        self.login(self.secretariat_user, browser)
        self.assert_no_factories_menu(browser, self.leaf_repofolder)

    @browsing
    def test_no_addable_types_in_dossier(self, browser):
        self.login(self.regular_user, browser)

        with ZODBStorageInReadonlyMode():
            browser.open(self.dossier)
            addable = factoriesmenu.addable_types()

        # XXX: Dossier shows an empty factories menu for some reason
        self.assertEqual([], addable)

    @browsing
    def test_no_addable_types_in_task(self, browser):
        self.login(self.regular_user, browser)
        self.assert_no_factories_menu(browser, self.task)


class TestEditActionsDisabledInReadOnly(IntegrationTestCase):

    def assert_no_edit_link(self, browser, context):
        edit_label = 'Edit'
        if context.portal_type in ('opengever.document.document', 'ftw.mail.mail'):
            edit_label = 'Edit metadata'

        with ZODBStorageInReadonlyMode():
            browser.open(context)
            edit_link = browser.find(edit_label)

        self.assertIsNone(edit_link)

    @browsing
    def test_no_edit_for_reporoot(self, browser):
        self.login(self.administrator, browser)
        self.assert_no_edit_link(browser, self.repository_root)

    @browsing
    def test_no_edit_for_repofolder(self, browser):
        self.login(self.administrator, browser)
        self.assert_no_edit_link(browser, self.leaf_repofolder)

    @browsing
    def test_no_edit_for_dossier(self, browser):
        self.login(self.regular_user, browser)
        self.assert_no_edit_link(browser, self.dossier)

    @browsing
    def test_no_edit_for_task(self, browser):
        self.login(self.regular_user, browser)

        open_task = create(
            Builder('task')
            .within(self.dossier)
            .having(issuer=self.dossier_responsible.id,
                    responsible=self.regular_user.id,
                    responsible_client='fa',
                    task_type='correction')
            .in_state('task-state-open'))

        self.assert_no_edit_link(browser, open_task)

    @browsing
    def test_no_edit_for_document(self, browser):
        self.login(self.regular_user, browser)
        self.assert_no_edit_link(browser, self.document)

    @browsing
    def test_no_edit_for_mail(self, browser):
        self.login(self.regular_user, browser)
        self.assert_no_edit_link(browser, self.mail_eml)


class TestWorkflowTransitionsDisabledInReadOnly(IntegrationTestCase):

    def get_menu_actions(self, browser, context):
        with ZODBStorageInReadonlyMode():
            browser.open(context)

        return editbar.menu_options('Actions')

    @browsing
    def test_no_wf_transitions_on_dossier(self, browser):
        self.login(self.regular_user, browser)
        actions = self.get_menu_actions(browser, self.dossier)

        self.assertEqual([
            'Cover (PDF)',
            'Export as Zip',
            'Print details (PDF)',
            'Properties'],
            actions)

    @browsing
    def test_no_wf_transitions_on_task(self, browser):
        self.login(self.regular_user, browser)
        with ZODBStorageInReadonlyMode():
            browser.open(self.task)

        self.assertFalse(editbar.visible())


class APITestMixin(object):

    def api_request(self, browser, context, endpoint):
        browser.open(context, headers=self.api_headers, view=endpoint)
        return browser.json

    def get_actions(self, browser, context):
        return self.api_request(browser, context, '@actions')

    def get_addable_types(self, browser, context):
        types = self.api_request(browser, context, '@types')
        return [t for t in types if t['addable']]

    def transition_ids(self, transitions):
        return [tn['@id'].split('@workflow/')[-1] for tn in transitions]

    def get_workflow(self, browser, context):
        return self.api_request(browser, context, '@workflow')

    def action_ids(self, actions):
        return [action['id'] for action in actions]

    def type_ids(self, types):
        return [type_['@id'].split('@types/')[-1] for type_ in types]


class TestAddActionsDisabledInReadOnlyAPI(IntegrationTestCase, APITestMixin):

    @browsing
    def test_no_addable_types_on_repofolder(self, browser):
        self.login(self.regular_user, browser)
        with ZODBStorageInReadonlyMode():
            types = self.get_addable_types(browser, self.leaf_repofolder)

        self.assertEqual([], self.type_ids(types))

    @browsing
    def test_no_addable_types_on_dossier(self, browser):
        self.login(self.regular_user, browser)
        with ZODBStorageInReadonlyMode():
            types = self.get_addable_types(browser, self.dossier)

        # XXX: Mail is special. Again.
        self.assertEqual([u'ftw.mail.mail'], self.type_ids(types))

    @browsing
    def test_no_addable_types_on_task(self, browser):
        self.login(self.regular_user, browser)
        with ZODBStorageInReadonlyMode():
            types = self.get_addable_types(browser, self.task)

        self.assertEqual([], self.type_ids(types))


class TestEditActionsDisabledInReadOnlyAPI(IntegrationTestCase, APITestMixin):

    @browsing
    def test_no_edit_action_on_reporoot(self, browser):
        self.login(self.administrator, browser)
        with ZODBStorageInReadonlyMode():
            actions = self.get_actions(browser, self.repository_root)

        self.assertNotIn('edit', self.action_ids(actions['object']))

    @browsing
    def test_no_edit_action_on_repofolder(self, browser):
        self.login(self.administrator, browser)
        with ZODBStorageInReadonlyMode():
            actions = self.get_actions(browser, self.leaf_repofolder)

        self.assertNotIn('edit', self.action_ids(actions['object']))

    @browsing
    def test_no_edit_action_on_dossier(self, browser):
        self.login(self.regular_user, browser)
        with ZODBStorageInReadonlyMode():
            actions = self.get_actions(browser, self.dossier)

        self.assertNotIn('edit', self.action_ids(actions['object']))

    @browsing
    def test_no_edit_action_on_task(self, browser):
        self.login(self.regular_user, browser)

        open_task = create(
            Builder('task')
            .within(self.dossier)
            .having(issuer=self.dossier_responsible.id,
                    responsible=self.regular_user.id,
                    responsible_client='fa',
                    task_type='correction')
            .in_state('task-state-open'))

        with ZODBStorageInReadonlyMode():
            actions = self.get_actions(browser, open_task)

        self.assertNotIn('edit', self.action_ids(actions['object']))

    @browsing
    def test_no_edit_action_on_document(self, browser):
        self.login(self.regular_user, browser)
        with ZODBStorageInReadonlyMode():
            actions = self.get_actions(browser, self.document)

        self.assertNotIn('edit', self.action_ids(actions['object']))

    @browsing
    def test_no_edit_action_on_mail(self, browser):
        self.login(self.regular_user, browser)
        with ZODBStorageInReadonlyMode():
            actions = self.get_actions(browser, self.mail_eml)

        self.assertNotIn('edit', self.action_ids(actions['object']))


class TestWorkflowTransitionsDisabledInReadOnlyAPI(IntegrationTestCase, APITestMixin):

    @browsing
    def test_no_wf_transitions_on_dossier(self, browser):
        self.login(self.regular_user, browser)
        with ZODBStorageInReadonlyMode():
            workflow = self.get_workflow(browser, self.dossier)

        self.assertEqual([], self.transition_ids(workflow['transitions']))

    @browsing
    def test_no_wf_transitions_on_task(self, browser):
        self.login(self.regular_user, browser)
        with ZODBStorageInReadonlyMode():
            workflow = self.get_workflow(browser, self.task)

        self.assertEqual([], self.transition_ids(workflow['transitions']))
