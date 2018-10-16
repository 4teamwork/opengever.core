from ftw.bumblebee.interfaces import IBumblebeeJournal
from ftw.bumblebee.journal import BumblebeeJournal as OriginalBumblebeeJournal
from opengever.bumblebee.journal import BumblebeeLogfileJournal
from opengever.testing import IntegrationTestCase


class TestBumblebeeLogfileJournal(IntegrationTestCase):

    features = ('bumblebee', )

    def test_logfile_journal_doesnt_write_persistent_data(self):
        self.login(self.administrator)

        original_journal = OriginalBumblebeeJournal(self.document)

        self.assertIsInstance(IBumblebeeJournal(self.document), BumblebeeLogfileJournal)

        len_before = len(list(original_journal.items()))
        IBumblebeeJournal(self.document).add('message', data='foo')
        len_after = len(list(original_journal.items()))

        self.assertEqual(len_before, len_after)
