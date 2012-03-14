from datetime import date
from ftw.testing import MockTestCase
from opengever.mail.indexer import document_author, document_date, receipt_date
from opengever.mail.indexer import sortable_author, checked_out


class TestMailIndexers(MockTestCase):

    def test_checked_out(self):
        self.assertEqual(checked_out(None)(), '')

    def test_author_indexes(self):
        mail = self.stub()
        msg = self.stub()
        self.expect(mail.msg).result(msg)
        self.expect(msg.has_key('From')).result(True)
        self.expect(msg.get('From')).result(u'"Hugo Boss" <hugo.boss@boss.com>')
        self.replay()

        self.assertEqual(
            document_author(mail)(), '"Hugo Boss" &lt;hugo.boss@boss.com&gt;')

        self.assertEqual(
            sortable_author(mail)(), '"Hugo Boss" &lt;hugo.boss@boss.com&gt;')

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
