from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.ogds.base.utils import get_current_org_unit
from opengever.task.browser.delegate.vocabulary import attachable_documents_vocabulary
from opengever.testing import IntegrationTestCase
from plone import api
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility


class TestDelegateTaskToInbox(IntegrationTestCase):

    @browsing
    def test_delegate_to_inbox(self, browser):
        self.login(self.secretariat_user, browser)

        browser.open(self.task,
                     view='@@task_transition_controller',
                     data={'transition': 'task-transition-delegate'})

        form = browser.find_form_by_field('Responsibles')
        form.find_widget('Responsibles').fill(
            ['inbox:{}'.format(get_current_org_unit().id())])
        browser.css('#form-buttons-save').first.click()  # can't use submit()

        form = browser.find_form_by_field('Issuer')
        form.find_widget('Issuer').fill(self.dossier_responsible.getId())

        browser.css('#form-buttons-save').first.click()  # can't use submit()

        self.assertEqual(['1 subtasks were created.'],
                         statusmessages.info_messages())


class TestDelegateTaskForm(IntegrationTestCase):

    @browsing
    def test_delegate_creates_subtask(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.task, view='delegate_recipients')

        # step 1
        form = browser.find_form_by_field('Responsibles')
        form.find_widget('Responsibles').fill(self.dossier_responsible)
        browser.css('#form-buttons-save').first.click()

        # step 2
        browser.css('#form-buttons-save').first.click()

        self.assertEqual(['1 subtasks were created.'],
                         statusmessages.info_messages())

        subtask = self.task.objectValues()[-1]
        self.assertEqual(self.task.title, subtask.title)
        self.assertEqual('robert.ziegler', subtask.responsible)
        self.assertEqual('fa', subtask.responsible_client)
        self.assertEqual('task-state-open', api.content.get_state(subtask))
        self.assertEqual('task-15', subtask.id)

    @browsing
    def test_issuer_is_prefilled_with_current_user(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.task, view='delegate_recipients')

        form = browser.find_form_by_field('Responsibles')
        form.find_widget('Responsibles').fill(self.dossier_responsible)
        browser.css('#form-buttons-save').first.click()

        self.assertEqual(
            self.regular_user.getId(), browser.find('Issuer').value)

    @browsing
    def test_responsible_is_required(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.task, view='delegate_recipients')
        browser.css('#form-buttons-save').first.click()

        self.assertEqual(
            ['Required input is missing.'],
            browser.css('#formfield-form-widgets-responsibles .error').text)

    @browsing
    def test_teams_are_selectable_as_responsible(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.task, view='delegate_recipients')

        form = browser.find_form_by_field('Responsibles')
        form.find_widget('Responsibles').fill(['team:1'])
        browser.css('#form-buttons-save').first.click()  # can't use submit()

        form = browser.find_form_by_field('Issuer')
        form.find_widget('Issuer').fill(self.dossier_responsible.getId())
        browser.css('#form-buttons-save').first.click()  # can't use submit()

        self.assertEqual(
            ['1 subtasks were created.'], statusmessages.info_messages())


class TestAttachableDocumentsVocabulary(IntegrationTestCase):

    def test_attachable_documents_vocabulary_lists_contained_and_related_documents(self):
        self.login(self.regular_user)
        intids = getUtility(IIntIds)
        terms = attachable_documents_vocabulary(self.task)

        self.assertItemsEqual(
            [el.UID() for el in [self.document, self.taskdocument]],
            [term.token for term in terms])
        self.assertItemsEqual(
            [str(intids.getId(el)) for el in [self.document, self.taskdocument]],
            [term.value for term in terms])
