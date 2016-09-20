from opengever.base.source import RepositoryPathSourceBinder
from opengever.journal import _
from opengever.journal.entry import ManualJournalEntry
from plone.directives import form
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from z3c.form.field import Fields
from z3c.form.form import AddForm
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema


class IManualJournalEntry(form.Schema):

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
            vocabulary=u'opengever.contact.ContactsVocabulary'),
        required=False,
    )

    related_documents = RelationList(
        title=_(u'label_related_documents', default=u'Related Documents'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Related",
            source=RepositoryPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    'object_provides':
                    ['opengever.repository.repositoryroot.IRepositoryRoot',
                     'opengever.repository.repositoryfolder.IRepositoryFolderSchema',
                     'opengever.dossier.behaviors.dossier.IDossierMarker',
                     'opengever.document.document.IDocumentSchema',
                     'ftw.mail.mail.IMail', ]
                }),
            ),
        required=False,
    )


class ManualJournalEntryAddForm(AddForm):
    label = _(u'label_add_journal_entry', default=u'Add journal entry')
    fields = Fields(IManualJournalEntry)

    fields['contacts'].widgetFactory = AutocompleteMultiFieldWidget

    def createAndAdd(self, data):
        entry = ManualJournalEntry(self.context,
                                   data.get('category'),
                                   data.get('comment'),
                                   data.get('contacts'),
                                   data.get('related_documents'))
        entry.save()
        return entry

    def nextURL(self):
        return '{}#journal'.format(self.context.absolute_url())
