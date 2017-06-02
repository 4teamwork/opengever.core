from ftw.keywordwidget.widget import KeywordWidget
from opengever.base.source import DossierPathSourceBinder
from opengever.contact.sources import ContactsSourceBinder
from opengever.journal import _
from opengever.journal.entry import ManualJournalEntry
from plone.autoform.widgets import ParameterizedWidget
from plone.directives import form
from z3c.form.field import Fields
from z3c.form.form import AddForm
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema


class IManualJournalEntry(form.Schema):
    """Provide a z3c.form.Schema to enter a manual journal entry."""

    category = schema.Choice(
        title=_(u'label_category', default=u'Category'),
        vocabulary='opengever.journal.manual_entry_categories',
        required=True,
    )

    comment = schema.Text(
        title=_(u'label_comment', default=u'Comment'),
        required=False,
    )

    contacts = schema.List(
        title=_(u'label_contacts', default=u'Contacts'),
        value_type=schema.Choice(
            source=ContactsSourceBinder()),
        required=False,
    )

    related_documents = RelationList(
        title=_(u'label_related_documents', default=u'Related Documents'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Related",
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    'object_provides':
                    ['opengever.dossier.behaviors.dossier.IDossierMarker',
                     'opengever.document.document.IDocumentSchema',
                     'opengever.task.task.ITask',
                     'ftw.mail.mail.IMail']
                }),
            ),
        required=False,
    )


class ManualJournalEntryAddForm(AddForm):
    """Provide a z3c.form to enter a manual journal entry."""

    label = _(u'label_add_journal_entry', default=u'Add journal entry')
    fields = Fields(IManualJournalEntry)

    fields['contacts'].widgetFactory = ParameterizedWidget(
        KeywordWidget,
        async=True
    )

    def createAndAdd(self, data):
        contacts, users = self.split_contacts_and_users(data.get('contacts'))
        entry = ManualJournalEntry(self.context,
                                   data.get('category'),
                                   data.get('comment'),
                                   contacts,
                                   users,
                                   data.get('related_documents'))
        entry.save()
        return entry

    def split_contacts_and_users(self, items):
        """Spliting up the contact list, in to a list of contact objects
        and a list of adapted users.
        """
        contacts = []
        users = []
        for item in items:
            if item.is_adapted_user:
                users.append(item)
            else:
                contacts.append(item)

        return contacts, users

    def nextURL(self):
        return '{}#journal'.format(self.context.absolute_url())
