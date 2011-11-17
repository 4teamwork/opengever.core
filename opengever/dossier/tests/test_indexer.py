from opengever.dossier.businesscase import IBusinessCaseDossier
from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING
# from plone.dexterity.interfaces import IDexterityFTI
# from zope.component import createObject
# from zope.component import queryUtility
import unittest2 as unittest


class Testindexers(unittest.TestCase):

    layer = OPENGEVER_DOSSIER_INTEGRATION_TESTING

    # def test_containing_subdossierx(self):

    # XXX
    # Don't work yet because its not possible to access to the dependent vocabulary from opengever.octopus.tentacle
    # def test_view(self):
    #     self.folder.invokeFactory('opengever.dossier.businesscasedossier', 'dossier1')
    #     d1 = self.folder['dossier1']
    #     view = d1.restrictedTraverse('@@view')
    #     self.failUnless(view())
