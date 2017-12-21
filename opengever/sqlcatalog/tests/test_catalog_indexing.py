from opengever.sqlcatalog.interfaces import ISQLCatalog
from opengever.testing import IntegrationTestCase
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestIndexing(IntegrationTestCase):

    def test_documents_are_indexed(self):
        self.login(self.regular_user)
        record = getUtility(ISQLCatalog).get_record_for(self.document)
        self.assertEquals(u'plone:1014073300', record.oguid)
        self.assertEquals(u'plone', record.admin_unit_id)
        self.assertEquals(u'createtreatydossiers000000000002', record.uuid)
        self.assertEquals(u'Vertr\xe4gsentwurf', record.title)
        self.assertEquals(
            u'/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-4',
            record.absolute_path)
        self.assertEquals(
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-4',
            record.relative_path)

    def test_get_object(self):
        self.login(self.regular_user)
        record = getUtility(ISQLCatalog).get_record_for(self.document)
        self.assertEquals(self.document, record.get_object())

    def test_reindexed_when_modified(self):
        self.login(self.regular_user)
        record = getUtility(ISQLCatalog).get_record_for(self.document)
        self.assertEquals(u'Vertr\xe4gsentwurf', record.title)
        self.document.setTitle('N\xc3\xb6ier Titel')
        notify(ObjectModifiedEvent(self.document))
        self.assertEquals(u'N\xf6ier Titel', record.title)
