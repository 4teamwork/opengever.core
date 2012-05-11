from Products.CMFCore.utils import getToolByName
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
import transaction
import unittest2 as unittest


def obj2brain(obj):
    catalog = getToolByName(obj, 'portal_catalog')
    query = {'path': {'query': '/'.join(obj.getPhysicalPath()),
                  'depth': 0}}
    brains = catalog(query)
    if len(brains) == 0:
        raise Exception('Not in catalog: %s' % obj)
    else:
        return brains[0]

def getindexDataForObj(obj):
    catalog = getToolByName(obj, 'portal_catalog')
    return catalog.getIndexDataForRID(obj2brain(obj).getRID())


class Testindexers(unittest.TestCase):

    layer = OPENGEVER_DOSSIER_INTEGRATION_TESTING

    def test_containing_dossier(self):
        portal = self.layer['portal']
        portal.invokeFactory('opengever.dossier.businesscasedossier', 'dossier')
        dossier = portal.get('dossier')
        IOpenGeverBase(dossier).title=u"Testd\xf6ssier XY"
        dossier.reindexObject()

        dossier.invokeFactory('opengever.dossier.businesscasedossier', 'subdossier')
        subdossier = dossier.get('subdossier')
        IOpenGeverBase(subdossier).title=u"Subd\xf6ssier XY"
        subdossier.reindexObject()

        subdossier.invokeFactory('opengever.document.document', 'document')
        document = subdossier.get('document')
        document.reindexObject()

        self.assertEquals(
            obj2brain(subdossier).containing_dossier,
            'Testd\xc3\xb6ssier XY')

        self.assertEquals(
            obj2brain(document).containing_dossier,
            'Testd\xc3\xb6ssier XY')

        #check subscriber for catch editing maindossier titel
        IOpenGeverBase(dossier).title=u"Testd\xf6ssier CHANGED"
        dossier.reindexObject()
        notify(
            ObjectModifiedEvent(dossier, Attributes(Interface, 'IOpenGeverBase.title')))

        self.assertEquals(
            obj2brain(subdossier).containing_dossier,
            'Testd\xc3\xb6ssier CHANGED')
        self.assertEquals(
            obj2brain(document).containing_dossier,
            'Testd\xc3\xb6ssier CHANGED')

        transaction.commit()

    def test_is_subdossier_index(self):
        portal = self.layer['portal']

        dossier = portal.get('dossier')
        subdossier = dossier.get('subdossier')

        self.assertEquals(getindexDataForObj(dossier).get('is_subdossier'), False)
        self.assertEquals(getindexDataForObj(subdossier).get('is_subdossier'), True)

    def test_containing_subdossier(self):
        portal = self.layer['portal']
        subdossier = portal.get('dossier').get('subdossier')
        self.assertEquals(obj2brain(subdossier).containing_subdossier, '')
        self.assertEquals(
            obj2brain(subdossier.get('document')).containing_subdossier,
            'Subd\xc3\xb6ssier XY')

        #check subscriber for catch editing subdossier titel
        IOpenGeverBase(subdossier).title=u'Subd\xf6ssier CHANGED'
        subdossier.reindexObject()
        notify(
            ObjectModifiedEvent(subdossier, Attributes(Interface, 'IOpenGeverBase.title')))

        self.assertEquals(obj2brain(subdossier).containing_subdossier,u'')
        self.assertEquals(
            obj2brain(subdossier.get('document')).containing_subdossier,
            'Subd\xc3\xb6ssier CHANGED')

    def test_filing_no(self):
        portal = self.layer['portal']
        dossier = portal.get('dossier')

        # no number, no prefix
        self.assertEquals(getindexDataForObj(dossier).get('filing_no'), None)
        self.assertEquals(getindexDataForObj(dossier).get('searchable_filing_no'), '')

        # no number only prefix
        IDossier(dossier).filing_prefix = 'directorate'
        dossier.reindexObject()
        self.assertEquals(getindexDataForObj(dossier).get('filing_no'),
                          'OG-Directorate-?')
        self.assertEquals(getindexDataForObj(dossier).get('searchable_filing_no'),
                          ['og', 'directorate'])

        # with number and prefix
        IDossier(dossier).filing_no = 'SKA ARCH-Administration-2012-3'
        dossier.reindexObject()
        self.assertEquals(getindexDataForObj(dossier).get('filing_no'),
            'SKA ARCH-Administration-2012-3')
        self.assertEquals(getindexDataForObj(dossier).get('searchable_filing_no'),
                          ['ska', 'arch', 'administration', '2012', '3'])


