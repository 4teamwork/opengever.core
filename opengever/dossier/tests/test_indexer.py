from ftw.builder import Builder
from ftw.builder import create
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from opengever.testing import obj2brain
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
import transaction


class TestIndexers(FunctionalTestCase):

    def setUp(self):
        super(TestIndexers, self).setUp()
        self.grant('Contributor')

        self.dossier = create(Builder("dossier").titled(u"Testd\xf6ssier XY"))
        self.dossier.reindexObject()

        self.subdossier = create(Builder("dossier")
                                 .within(self.dossier)
                                 .titled(u"Subd\xf6ssier XY"))
        self.subdossier.reindexObject()

        self.document = create(Builder("document").within(self.subdossier))
        self.document.reindexObject()

    def test_containing_dossier(self):
        self.assertEquals(
            obj2brain(self.subdossier).containing_dossier,
            'Testd\xc3\xb6ssier XY')

        self.assertEquals(
            obj2brain(self.document).containing_dossier,
            'Testd\xc3\xb6ssier XY')

        #check subscriber for catch editing maindossier titel
        IOpenGeverBase(self.dossier).title=u"Testd\xf6ssier CHANGED"
        self.dossier.reindexObject()
        notify(
            ObjectModifiedEvent(self.dossier, Attributes(Interface, 'IOpenGeverBase.title')))

        self.assertEquals(
            obj2brain(self.subdossier).containing_dossier,
            'Testd\xc3\xb6ssier CHANGED')
        self.assertEquals(
            obj2brain(self.document).containing_dossier,
            'Testd\xc3\xb6ssier CHANGED')

        transaction.commit()

    def test_is_subdossier_index(self):
        self.assertEquals(index_data_for(self.dossier).get('is_subdossier'), False)
        self.assertEquals(index_data_for(self.subdossier).get('is_subdossier'), True)

    def test_containing_subdossier(self):
        self.assertEquals(obj2brain(self.subdossier).containing_subdossier, '')
        self.assertEquals(
            obj2brain(self.document).containing_subdossier,
            'Subd\xc3\xb6ssier XY')

        #check subscriber for catch editing subdossier titel
        IOpenGeverBase(self.subdossier).title=u'Subd\xf6ssier CHANGED'
        self.subdossier.reindexObject()
        notify(
            ObjectModifiedEvent(self.subdossier, Attributes(Interface, 'IOpenGeverBase.title')))

        self.assertEquals(obj2brain(self.subdossier).containing_subdossier,u'')
        self.assertEquals(
            obj2brain(self.document).containing_subdossier,
            'Subd\xc3\xb6ssier CHANGED')

    def test_filing_no(self):
        # no number, no prefix
        self.assertEquals(index_data_for(self.dossier).get('filing_no'), None)
        self.assertEquals(index_data_for(self.dossier).get('searchable_filing_no'), '')

        # no number only prefix
        IDossier(self.dossier).filing_prefix = 'directorate'
        self.dossier.reindexObject()
        self.assertEquals(index_data_for(self.dossier).get('filing_no'),
                          'OG-Directorate-?')
        self.assertEquals(index_data_for(self.dossier).get('searchable_filing_no'),
                          ['og', 'directorate'])

        # with number and prefix
        IDossier(self.dossier).filing_no = 'SKA ARCH-Administration-2012-3'
        self.dossier.reindexObject()
        self.assertEquals(index_data_for(self.dossier).get('filing_no'),
            'SKA ARCH-Administration-2012-3')
        self.assertEquals(index_data_for(self.dossier).get('searchable_filing_no'),
                          ['ska', 'arch', 'administration', '2012', '3'])
