from Products.CMFCore.utils import getToolByName
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
import unittest2 as unittest
import transaction


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
        IOpenGeverBase(dossier).title=u"Testdossier XY"
        dossier.reindexObject()

        dossier.invokeFactory('opengever.dossier.businesscasedossier', 'subdossier')
        subdossier = dossier.get('subdossier')
        subdossier.reindexObject()

        subdossier.invokeFactory('opengever.document.document', 'document')
        document = subdossier.get('document')
        document.reindexObject()

        self.assertEquals(obj2brain(subdossier).containing_dossier,u'Testdossier XY')

        self.assertEquals(obj2brain(document).containing_dossier, u'Testdossier XY')

        #check subscriber for catch editing maindossier titel
        IOpenGeverBase(dossier).title=u"Testdossier CHANGED"
        dossier.reindexObject()
        notify(
            ObjectModifiedEvent(dossier, Attributes(Interface, 'IOpenGeverBase.title')))

        self.assertEquals(obj2brain(subdossier).containing_dossier,u'Testdossier CHANGED')
        self.assertEquals(obj2brain(document).containing_dossier, u'Testdossier CHANGED')

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
        self.assertEquals(obj2brain(subdossier.get('document')).containing_subdossier, '')
