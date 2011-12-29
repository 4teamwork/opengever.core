from Products.CMFCore.utils import getToolByName
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
import unittest2 as unittest


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

        dossier.invokeFactory('opengever.document.document', 'document')
        document = dossier.get('document')
        document.reindexObject()

        catalog = getToolByName(portal, 'portal_catalog')

        self.assertEquals(
            catalog(
                path='/'.join(subdossier.getPhysicalPath()))[0].containing_dossier,
            u'Testdossier XY'
            )

        self.assertEquals(
            catalog(
                path='/'.join(document.getPhysicalPath()))[0].containing_dossier,
            u'Testdossier XY'
            )

        #check subscriber for catch editing maindossier titel
        IOpenGeverBase(dossier).title=u"Testdossier CHANGED"
        dossier.reindexObject()
        notify(
            ObjectModifiedEvent(dossier, Attributes(Interface, 'IOpenGeverBase.title')))

        self.assertEquals(
            catalog(
                path='/'.join(subdossier.getPhysicalPath()))[0].containing_dossier,
            u'Testdossier CHANGED'
            )

        self.assertEquals(
            catalog(
                path='/'.join(document.getPhysicalPath()))[0].containing_dossier,
            u'Testdossier CHANGED'
            )

