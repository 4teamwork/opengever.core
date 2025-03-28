from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized
import transaction
import unittest


class TestTaskWorkflowAddingDocumentsAndMails(FunctionalTestCase):

    def setUp(self):
        super(TestTaskWorkflowAddingDocumentsAndMails, self).setUp()
        self.dossier = create(Builder('dossier').titled(u'Dossier'))

        self.task = create(Builder("task")
                           .within(self.dossier)
                           .titled(u'Aufgabe f\xfcr Hans')
                           .having(task_type='comment',
                                   deadline=datetime(2010, 1, 1),
                                   issuer=TEST_USER_ID,
                                   responsible=TEST_USER_ID,
                                   responsible_client='org-unit-1')
                           .with_text(content=u'Text f\xfcr Aufgabe'))

    def click_task_button(self, browser, button_class, save_and_reload=True):
        """Visits the overview view on `self.task`, clicks the button
        identified by the CSS class `button_class`, and, if `save_and_reload`
        is True, saves the form and reloads the overview view.
        """
        self.visit_overview(browser)
        button = browser.css('.{}'.format(button_class)).first
        button.click()
        if save_and_reload:
            browser.forms.get('form').save()
            self.visit_overview(browser)

    def visit_overview(self, browser, task=None):
        if task is None:
            task = self.task
        browser.open(self.task, view='tabbedview_view-overview')

    @browsing
    def test_adding_doc_in_state_open_allowed(self, browser):
        browser.login()

        browser.visit(self.task, view='++add++opengever.document.document')
        form = browser.fill({'Title': 'foobar'})
        form.save()

    @unittest.skip("Raises Unauthorized from some reason (only in test).")
    @browsing
    def test_adding_mail_in_state_open_allowed(self, browser):
        browser.login()

        browser.visit(self.task, view='++add++ftw.mail.mail')
        form = browser.fill({'Title': 'foobar'})
        form.save()

    @browsing
    def test_adding_doc_in_state_tested_and_closed_not_allowed(self, browser):
        browser.login()

        # Set task to state 'tested-and-closed'
        self.click_task_button(browser, 'close')

        browser.visit(self.task, view='++add++opengever.document.document')
        form = browser.fill({'Title': 'foobar'})

        # https://github.com/4teamwork/opengever.core/issues/2923
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized) as cm:
            form.save()
        self.assertEquals("Cannot create opengever.document.document",
                          cm.exception.message)

    @browsing
    def test_adding_mail_in_state_tested_and_closed_not_allowed(self, browser):
        browser.login()

        # Set task to state 'tested-and-closed'
        self.click_task_button(browser, 'close')

        browser.visit(self.task, view='++add++ftw.mail.mail')
        form = browser.fill({'Title': 'foobar'})

        # https://github.com/4teamwork/opengever.core/issues/2923
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized) as cm:
            form.save()

        self.assertEquals("Cannot create ftw.mail.mail",
                          cm.exception.message)


class TestTaskWorkflow(FunctionalTestCase):

    def setUp(self):
        super(TestTaskWorkflow, self).setUp()
        self.wf_tool = getToolByName(self.portal, 'portal_workflow')

    @browsing
    def test_document_in_a_closed_tasks_are_still_editable(self, browser):
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID,
                              responsible_client=u'org-unit-1',
                              responsible=TEST_USER_ID,)
                      .in_state('task-state-tested-and-closed'))

        document = create(Builder('document')
                          .titled(u'Letter for Peter')
                          .within(task))

        browser.login().open(document, view='edit')
        browser.fill({'Title': 'New Title'})
        browser.click_on('Save')

        self.assertEquals(['Changes saved'], info_messages())

    @browsing
    def test_editing_document_inside_a_task_inside_a_closed_dossier_raise_unauthorized(self, browser):
        self.grant('Administrator')
        dossier = create(Builder('dossier'))

        task = create(Builder('task')
                      .within(dossier)
                      .having(issuer=TEST_USER_ID,
                              responsible_client=u'org-unit-1',
                              responsible=TEST_USER_ID)
                      .in_state('task-state-tested-and-closed'))

        document = create(Builder('document')
                          .titled(u'Letter for Peter')
                          .within(task))

        self.wf_tool.doActionFor(dossier, 'dossier-transition-resolve')
        transaction.commit()

        with browser.expect_unauthorized():
            browser.login().open(document, view='edit')

    def test_deleting_task_is_only_allowed_for_managers(self):
        task = create(Builder('task')
                      .having(responsible_client=u'org-unit-1'))

        acl_users = api.portal.get_tool('acl_users')
        valid_roles = list(acl_users.portal_role_manager.valid_roles())
        valid_roles.remove('Manager')
        self.grant(*valid_roles)

        with self.assertRaises(Unauthorized):
            api.content.delete(obj=task)
