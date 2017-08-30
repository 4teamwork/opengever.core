from ftw.keywordwidget.widget import KeywordWidget
from opengever.base.source import DossierPathSourceBinder
from opengever.contact import is_contact_feature_enabled
from opengever.contact.sources import ContactsSourceBinder
from opengever.journal import _
from opengever.journal.entry import ManualJournalEntry
from plone.autoform.widgets import ParameterizedWidget
from plone.dexterity.i18n import MessageFactory as pd_mf
from plone.directives import form
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.form import AddForm
from z3c.form.i18n import MessageFactory as z3c_mf
from z3c.form.interfaces import HIDDEN_MODE
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

    def updateWidgets(self, prefix=None):
        super(ManualJournalEntryAddForm, self).updateWidgets(prefix=prefix)
        if not is_contact_feature_enabled():
            self.widgets['contacts'].mode = HIDDEN_MODE

    @button.buttonAndHandler(z3c_mf('Add'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    @button.buttonAndHandler(pd_mf(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        return self.request.RESPONSE.redirect(
            '{}#journal'.format(self.context.absolute_url()))

    def updateActions(self):
        super(ManualJournalEntryAddForm, self).updateActions()
        self.actions['add'].addClass("context")

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
