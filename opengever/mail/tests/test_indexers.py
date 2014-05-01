from collective.dexteritytextindexer.interfaces import \
    IDynamicTextIndexExtender
from datetime import date
from ftw.mail.mail import IMail
from ftw.testing import MockTestCase
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.mail.indexer import document_author, document_date, receipt_date
from opengever.mail.indexer import sortable_author, checked_out
from zope.component import getAdapters, getAdapter
from zope.interface import Interface
from grokcore.component.testing import grok


class TestMailIndexers(MockTestCase):

    def setUp(self):
        super(TestMailIndexers, self).setUp()
        grok('opengever.mail.indexer')

    def test_checked_out(self):
        self.assertEqual(checked_out(None)(), '')

    def test_author_indexes(self):
        mail = self.stub()
        msg = self.stub()

        self.expect(mail.msg).result(msg)
        self.expect(msg.has_key('From')).result(True)
        self.expect(msg.get('From')).result(
            u'"Hugo Boss" <hugo.boss@boss.com>')
        self.replay()

        # ftw.mail removes quotes around name in 'From:'
        self.assertEqual(
            document_author(mail)(),
            'Hugo Boss &lt;hugo.boss@boss.com&gt;')

        self.assertEqual(
            sortable_author(mail)(),
            'Hugo Boss &lt;hugo.boss@boss.com&gt;')

    def test_author_indexes_with_bad_from_header(self):
        mail = self.stub()
        msg = self.stub()

        self.expect(mail.msg).result(msg)
        self.expect(msg.has_key('From')).result(True)
        self.expect(msg.get('From')).result(
            'Patrick Hengartner </O=KANTON ZUG/OU=EXCHANGE ADMINISTRATIVE GROUP\n (FYDIBOHF23SPDLT)/CN=RECIPIENTS/CN=HEPA>')

        self.replay()

        self.assertEqual(
            document_author(mail)(),
            'Patrick Hengartner')

        self.assertEqual(
            sortable_author(mail)(),
            'Patrick Hengartner')

    def test_date_indexer(self):
        mail = self.stub()
        msg = self.stub()

        self.expect(mail.msg).result(msg)
        self.expect(msg.has_key('Date')).result(True)
        self.expect(msg.get('Date')).result('Thu, 16 Feb 2012 17:16:03 +0100')
        self.replay()

        self.assertEqual(
            document_date(mail)(),
            date(2012, 2, 16))

        self.assertEqual(
            receipt_date(mail)(),
            date(2012, 2, 16))

    def test_reference_number(self):
        mail = self.providing_stub([IMail, ])

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
