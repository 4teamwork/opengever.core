from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.PloneTestCase.ptc import PloneTestCase
from datetime import datetime
from opengever.document.persistence import DCQueue
from opengever.document.tests.layer import CLayer
from persistent.dict import PersistentDict
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.publisher.browser import TestRequest
import unittest


class TestDocucomposer(PloneTestCase):

    layer = CLayer

    def test_create_document_with_file(self):

        queue = DCQueue(self.portal)
        user = getSecurityManager().getUser()

        intids = getUtility( IIntIds )

        data = PersistentDict({'title': 'Test Document',
                               'owner': user.getId(),
                               'intid': intids.getId(self.folder),
                               'creation_date': DateTime(),
                               'IRelatedDocuments.relatedItems': [],
                               'IClassification.public_trial_statement': None,
                               'receipt_date': None,
                               'foreign_reference': None,
                               'description': u'fasdf',
                               'document_author': u'zopemaster',
                               'IClassification.public_trial': u'unchecked',
                               'delivery_date': None,
                               'IClassification.privacy_layer': u'no',
                               'IClassification.classification':
                                   u'unprotected',
                               'paper_form': True,
                               'file': None,
                               'keywords': (),
                               'document_type': None,
                               'preserved_as_paper': True,
                               'document_date': datetime.now()})

        token = queue.appendDCDoc(data)

        request = TestRequest(file='', filename='test.doc', token=token)
        view = getMultiAdapter((self.portal, request),
                               name=u'create_document_with_file')

        url = view.render()
        doc = self.folder['document-1']
        self.assertEquals(url, doc.absolute_url())

        # check the paper form workaround (see docucomposer.py l. 136)
        self.assertEquals(doc.paper_form, False)

        # check the document icon
        self.assertEquals(doc.file.contentType, 'application/msword')

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
