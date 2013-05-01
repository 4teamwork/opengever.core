from ftw.testing import MockTestCase
from opengever.task.browser.complete import ICompleteSuccessorTaskSchema
from opengever.task.browser.complete import NoCheckedoutDocsValidator
from opengever.task.task import ITask
from plone.uuid.interfaces import IUUID, IAttributeUUID
from zope.app.intid.interfaces import IIntIds
from zope.interface import Invalid
from zope.schema import getFields


class TestTaskCompletion(MockTestCase):

    def test_nocheckedout_docs_validator(self):

        uuidtocatalogbrain = self.mocker.replace(
            'plone.app.uuid.utils.uuidToCatalogBrain')

        intids = self.stub()
        self.mock_utility(intids, IIntIds)

        uuid_adapter = self.stub()
        self.mock_adapter(uuid_adapter, IUUID, [IAttributeUUID, ])

        task1 = self.stub()
        request = self.stub()

        doc1 = self.providing_stub([IUUID])
        self.expect(doc1.title).result('Doc 1')
        self.expect(doc1.checked_out).result('hugo.boss')
        self.expect(uuid_adapter(doc1)).result(111)
        self.expect(intids.getObject(111)).result(doc1)
        self.expect(uuidtocatalogbrain(doc1)).result(doc1).count(0, None)

        doc2 = self.providing_stub([IUUID])
        self.expect(doc2.title).result('Doc 2')
        self.expect(doc2.checked_out).result(None)
        self.expect(uuid_adapter(doc2)).result(222)
        self.expect(intids.getObject(222)).result(doc2)
        self.expect(uuidtocatalogbrain(doc2)).result(doc2).count(0, None)

        doc3 = self.providing_stub([IUUID])
        self.expect(doc3.title).result('Doc 3')
        self.expect(doc3.checked_out).result('james.bond')
        self.expect(uuid_adapter(doc3)).result(333)
        self.expect(intids.getObject(333)).result(doc3)
        self.expect(uuidtocatalogbrain(doc3)).result(doc3).count(0, None)

        self.replay()

        field = getFields(ICompleteSuccessorTaskSchema).get('documents')
        validator = NoCheckedoutDocsValidator(task1, request, None, field,
                                              None)

        # no docs selected
        validator.validate([])

        # checked out doc selected
        with self.assertRaises(Invalid):
            validator.validate(['111', ])

        # no checked out doc selected
        validator.validate(['222'])

        # mutlitple checked out docs selected
        with self.assertRaises(Invalid):
            validator.validate(['111', '222', '333'])

        # check also for relation list field
        field = getFields(ITask).get('relatedItems')
        validator = NoCheckedoutDocsValidator(
            task1, request, None, field, None)

        validator.validate([doc2, ])

        with self.assertRaises(Invalid):
            validator.validate([doc1, doc2, doc3])

        # check also without a value
        validator.validate(None)
