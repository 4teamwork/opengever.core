from collective.indexing.interfaces import IIndexQueueProcessor
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from zope.interface import implementer


@implementer(IIndexQueueProcessor)
class DemoIndexQueueProcessor(object):

    reindex_log = []
    unindex_log = []
    index_log = []

    def index(self, obj, attributes=None):
        self.index_log.append((IUUID(obj), attributes))

    def reindex(self, obj, attributes=None):
        self.reindex_log.append((IUUID(obj), attributes))

    def unindex(self, obj):
        self.unindex_log.append(IUUID(obj))

    def begin(self):
        pass

    def commit(self):
        pass

    def abort(self):
        pass


class TestCollectiveIndexingActive(IntegrationTestCase):

    def test_pluggable_index_queue_processors(self):
        self.login(self.regular_user)
        self.layer['load_zcml_string']("""
            <configure xmlns="http://namespaces.zope.org/zope">
                <utility
                     provides="collective.indexing.interfaces.IIndexQueueProcessor"
                     name="demo"
                     factory="opengever.testing.tests.test_collective_indexing_active.DemoIndexQueueProcessor"
                     />
            </configure>
        """)

        self.document.unindexObject()
        self.assertEqual(
            [IUUID(self.document)],
            DemoIndexQueueProcessor.unindex_log)

        self.document.indexObject()
        self.assertEqual(
            [(IUUID(self.document), None)],
            DemoIndexQueueProcessor.index_log)

        self.document.reindexObject(idxs=['sortable_title'])
        self.assertEqual(
            [(IUUID(self.document), ('sortable_title',))],
            DemoIndexQueueProcessor.reindex_log)
