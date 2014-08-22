from ftw.upgrade import UpgradeStep
from opengever.journal.handlers import journal_entry_factory
from opengever.mail import _


def create_initial_journal_entry(mail):
    title = _(
        u'label_journal_initialized',
        default=u'Journal initialized')
    journal_entry_factory(mail, 'Journal initialized', title)


class CreateInitialJournalEntry(UpgradeStep):

    def __call__(self):
        query = {'portal_type': 'ftw.mail.mail'}
        for mail in self.objects(query, "Creating initial journal entry"):
            create_initial_journal_entry(mail)
