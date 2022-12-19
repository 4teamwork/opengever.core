from opengever.task.browser.complete import ICompleteSuccessorTaskSchema
from opengever.task.browser.complete import NoCheckedoutDocsValidator
from opengever.task.task import ITask
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.interface import Invalid


class TestNoCheckedOutDocsValidator(IntegrationTestCase):

    def test_nocheckedout_docs_validator_in_complete_form(self):
        self.login(self.regular_user)

        intids = getUtility(IIntIds)

        validator = NoCheckedoutDocsValidator(
            self.task, self.request, None,
            ICompleteSuccessorTaskSchema['documents'], None)

        # no docs selected
        validator.validate([])

        # no checked out doc selected
        validator.validate([intids.getId(self.document)])

        # checked out doc selected
        self.checkout_document(self.document)
        with self.assertRaises(Invalid):
            validator.validate([intids.getId(self.document)])

        # mutlitple checked out docs selected
        self.checkout_document(self.taskdocument)
        with self.assertRaises(Invalid):
            validator.validate([intids.getId(self.document),
                                intids.getId(self.taskdocument)])

    def test_nocheckedout_docs_validator_in_task_form(self):
        self.login(self.regular_user)

        validator = NoCheckedoutDocsValidator(
            self.task, self.request, None, ITask['relatedItems'], None)

        validator.validate([self.document, self.taskdocument])

        self.checkout_document(self.document)

        with self.assertRaises(Invalid):
            validator.validate([self.document, self.taskdocument])

        # check also without a value
        validator.validate(None)
