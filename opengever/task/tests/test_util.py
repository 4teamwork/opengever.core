from ftw.testing import MockTestCase
from opengever.task.util import get_documents_of_task


class TestGetDocumentsOfTask(MockTestCase):

    def setUp(self):
        self.catalog = self.stub()
        self.mock_tool(self.catalog, 'portal_catalog')

        self.membership = self.stub()
        self.mock_tool(self.membership, 'portal_membership')

    def _stub_catalog_obj(self):
        obj = self.stub()
        brain = self.stub()
        self.expect(brain.getObject()).result(obj)
        return brain, obj

    def _stub_related_obj(self, portal_type, allowed=True):
        obj = self.stub()
        rel = self.stub()
        self.expect(rel.to_object).result(obj)
        self.expect(obj.portal_type).result(portal_type)

        self.expect(self.membership.checkPermission(
                'View', obj)).result(allowed)
        return rel, obj

    def test_without_mails_is_default(self):
        task = self.mocker.mock()
        self.expect(task.getPhysicalPath()).result(
            ['', 'path', 'to', 'task'])

        rel1, obj1 = self._stub_related_obj('opengever.document.document')
        rel2, obj2 = self._stub_related_obj('opengever.document.document',
                                            allowed=False)
        rel3, obj3 = self._stub_related_obj('ftw.mail.mail')
        rel4, obj4 = self._stub_related_obj('Folder')
        self.expect(task.relatedItems).result([rel1, rel2, rel3, rel4])

        docbrain1, doc1 = self._stub_catalog_obj()
        expected_query = {'path': '/path/to/task',
                          'portal_type': ['opengever.document.document']}
        self.expect(self.catalog(expected_query)).result([docbrain1])

        self.replay()

        self.assertEqual(get_documents_of_task(task),
                         [doc1, obj1])

    def test_with_mails(self):
        task = self.mocker.mock()
        self.expect(task.getPhysicalPath()).result(
            ['', 'path', 'to', 'task'])

        rel1, obj1 = self._stub_related_obj('opengever.document.document')
        rel2, obj2 = self._stub_related_obj('opengever.document.document',
                                            allowed=False)
        rel3, obj3 = self._stub_related_obj('ftw.mail.mail')
        rel4, obj4 = self._stub_related_obj('Folder')
        self.expect(task.relatedItems).result([rel1, rel2, rel3, rel4])

        docbrain1, doc1 = self._stub_catalog_obj()
        mailbrain1, mail1 = self._stub_catalog_obj()
        expected_query = {'path': '/path/to/task',
                          'portal_type': ['opengever.document.document',
                                          'ftw.mail.mail']}
        self.expect(self.catalog(expected_query)).result(
            [docbrain1, mailbrain1])

        self.replay()

        self.assertEqual(get_documents_of_task(task, include_mails=True),
                         [doc1, mail1, obj1, obj3])
