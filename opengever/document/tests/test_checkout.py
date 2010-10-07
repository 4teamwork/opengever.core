import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.ptc import PloneTestCase
from opengever.document.tests.layer import CLayer

from opengever.document.document import IDocumentSchema
from opengever.document.staging.manager import ICheckinCheckoutManager

from ZODB.serialize import get_refs, ObjectWriter
from StringIO import StringIO
import transaction

class TestCheckout(PloneTestCase):

    layer = CLayer

    def test_folder_export_doesnt_include_parent(self):
        self.folder.invokeFactory('Folder', 'foo')
        foo = self.folder['foo']
        foo.invokeFactory('Folder', 'bar')
        bar = foo['bar']

        transaction.savepoint(optimistic=True)      # savepoint assigns oids
        # now let's export to a buffer and check the objects...
        exp = StringIO()
        self.folder._p_jar.exportFile(bar._p_oid, exp)
        self.failUnless('bar' in exp.getvalue())
        self.failIf('foo' in exp.getvalue())

    def test_document_export_doesnt_include_parent(self):
        self.folder.invokeFactory('opengever.dossier.businesscasedossier', 'foo')
        foo = self.folder['foo']
        foo.invokeFactory('opengever.document.document', 'bar')
        bar = foo['bar']

        transaction.savepoint(optimistic=True)      # savepoint assigns oids
        # now let's export to a buffer and check the objects...
        exp = StringIO()
        self.folder._p_jar.exportFile(bar._p_oid, exp)
        self.failUnless('bar' in exp.getvalue())
        self.failIf('foo' in exp.getvalue())

    def test_parent_reference_folder_document(self):
        self.folder.invokeFactory('Document', 'doc1')
        doc1 = self.folder['doc1']
        parent_oid = self.folder._p_oid
        ow = ObjectWriter(doc1)
        pickle = ow.serialize(doc1.aq_self)
        refs = get_refs(pickle)
        for ref in refs:
            self.failUnless(ref[0] != parent_oid)

    # def test_parent_reference(self):
    #     self.folder.invokeFactory('opengever.dossier.businesscasedossier', 'dossier1')
    #     dossier = self.folder['dossier1']
    #     dossier.invokeFactory('opengever.document.document', 'document1')
    #     d1 = dossier['document1']
    #     #import pdb; pdb.set_trace( )
    #     parent_oid = dossier._p_oid
    #     from ZODB.serialize import get_refs, ObjectWriter
    #     ow = ObjectWriter(d1)
    #     pickle = ow.serialize(d1.aq_self)
    #     refs = get_refs(pickle)
    #     for ref in refs:
    #         self.failUnless(ref[0] != parent_oid)
    #
    # def test_checkout(self):
    #     self.folder.invokeFactory('opengever.dossier.businesscasedossier', 'dossier1')
    #     dossier = self.folder['dossier1']
    #     dossier.invokeFactory('opengever.document.document', 'document1')
    #     d1 = dossier['document1']
    #     self.failUnless(IDocumentSchema.providedBy(d1))
    #
    #     #import transaction
    #     #transaction.commit()
    #     #oid = d1._p_oid
    #     #connection = d1._p_jar
    #     #load = connection._storage.load
    #     #pickle, serial = load(oid, connection._version)
    #     # parent_oid = dossier._p_oid
    #     # from ZODB.serialize import get_refs, ObjectWriter
    #     # ow = ObjectWriter(d1)
    #     # pickle = ow.serialize(d1.aq_self)
    #     # refs = get_refs(pickle)
    #     # for ref in refs:
    #     #     self.failUnless(ref[0] != parent_oid)
    #
    #     portal_repository = getToolByName(self.portal, 'portal_repository')
    #     portal_repository.setVersionableContentTypes(['opengever.document.document',])
    #     portal_repository.manage_setTypePolicies({'opengever.document.document':['version_on_revert',]})
    #     manager = ICheckinCheckoutManager(d1)
    #     wc = manager.checkout('testing checkout', show_status_message=False)



def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
