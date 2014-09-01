from collective.dexteritytextindexer.interfaces import \
    IDynamicTextIndexExtender
from ftw.mail.mail import IMail
from ftw.testing import MockTestCase
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.mail.indexer import checked_out
from zope.component import getAdapters, getAdapter
from zope.interface import Interface
from grokcore.component.testing import grok


class TestMailIndexers(MockTestCase):

    def setUp(self):
        super(TestMailIndexers, self).setUp()
        grok('opengever.mail.indexer')

    def test_checked_out(self):
        self.assertEqual(checked_out(None)(), '')

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
