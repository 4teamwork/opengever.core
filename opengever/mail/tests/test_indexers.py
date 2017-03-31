from collective.dexteritytextindexer.interfaces import IDynamicTextIndexExtender
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.mail import IMail
from ftw.testing import MockTestCase
from grokcore.component.testing import grok
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.mail.indexer import checked_out
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from zope.component import getAdapter
from zope.component import getAdapters
from zope.interface import Interface


class TestMailIndexers(FunctionalTestCase):

    def test_keywords_field_is_indexed_in_Subject_index(self):
        catalog = self.portal.portal_catalog

        create(Builder("mail")
               .having(keywords=(u'Keyword 1', u'Keyword with \xf6')))

        self.assertTrue(len(catalog(Subject=u'Keyword 1')),
                        'Expect one item with Keyword 1')
        self.assertTrue(len(catalog(Subject=u'Keyword with \xf6')),
                        u'Expect one item with Keyword with \xf6')

    def test_mail_searchable_text_contains_keywords(self):
        mail = create(
            Builder("mail")
            .having(keywords=(u'Pick me!', u'Keyw\xf6rd')))

        self.assertItemsEqual(
            [u'1', u'1', 'client1', 'no', 'subject', 'keyword', 'me', 'pick'],
            index_data_for(mail).get('SearchableText'))


class TestMailIndexersMock(MockTestCase):

    def setUp(self):
        super(TestMailIndexersMock, self).setUp()
        grok('opengever.mail.indexer')

    def test_checked_out(self):
        self.assertEqual(checked_out(None)(), '')

    def test_reference_number(self):
        mail = self.providing_stub([IMail, IDocumentMetadata])

        self.expect(mail.keywords).result([])

        ref_adapter = self.mocker.mock()
        self.expect(ref_adapter(mail)).result(ref_adapter)
        self.expect(
            ref_adapter.get_number()).result('OG 1.6 / 3 / 1')
        self.mock_adapter(
            ref_adapter, IReferenceNumber, [Interface])

        seq_adapter = self.mocker.mock()
        self.expect(seq_adapter.get_number(mail)).result('55')
        self.mock_utility(seq_adapter, ISequenceNumber)

        self.replay()

        extenders = getAdapters([mail, ], IDynamicTextIndexExtender)
        self.assertEquals(len([aa for aa in extenders]), 1)

        extender = getAdapter(
            mail, IDynamicTextIndexExtender, u'IOGMail')
        self.assertEquals(extender(), 'OG 1.6 / 3 / 1 55')
