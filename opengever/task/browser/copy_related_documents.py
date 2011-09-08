from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.utils import get_client_id
from opengever.ogds.base.vocabulary import ContactsVocabulary
from opengever.task import _
from plone.directives.form import Schema
from plone.z3cform import layout
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from zope import schema
from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory


class TargetClientsWithInboxVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of possible target clients. Related documents can be sent to
    inboxes of these clients. The user has to be assigned to these clients and
    he has to be in the inbox group of the clients.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.task.TargetClientsWithInboxVocabulary')

    def __call__(self, context):
        self.context = context
        return ContactsVocabulary.create_with_provider(self.key_value_provider)

    def key_value_provider(self):
        """yield the items

        key = client id
        value = client title
        """

        info = getUtility(IContactInformation)
        current_client_id = get_client_id()
        mtool = getToolByName(getSite(), 'portal_membership')
        member = mtool.getAuthenticatedMember()

        for client in info.get_assigned_clients():
            if current_client_id != client.client_id:
                inbox_group = client.inbox_group
                if inbox_group in member.getGroups():
                    yield (client.client_id,
                           client.title)


class ICopyRelatedDocumentsSchema(Schema):

    copy_documents = schema.Bool(
        title=_(u'label_copy_documents',
                default=u'Copy related documents to inbox of target client'),
        description=_(u'help_copy_documents',
                      default=u''),
        default=True)

    target_client = schema.Choice(
        title=_(u'label_target_client',
                default=u'Target client'),
        description=_(u'help_target_client',
                      default=u''),
        vocabulary=u'opengever.task.TargetClientsWithInboxVocabulary',
        required=True)


class CopyRelatedDocumentsForm(Form):
    fields = Fields(ICopyRelatedDocumentsSchema)
    label = _(u'title_copy_releated_documents',
              default=u'Copy related documents')
    ignoreContext = True

    @buttonAndHandler(_(u'button_copy', default=u'Copy'))
    def handle_copy(self, action):
        data, errors = self.extractData()
        if not self.available():
            IStatusMessage(self.request).addStatusMessage(_(
                    u'error_copying_related_documents_not_possible',
                    default=u"It's not possible to copy related documents."))
        if not errors and data['copy_documents']:
            self.copy_documents(data['target_client'])
            info = getUtility(IContactInformation)
            client = info.get_client_by_id(data['target_client'])
            IStatusMessage(self.request).addStatusMessage(
                _(u'info_copied_related_documents',
                  default=u'All related documents were copied to the inbox of '
                  'the client ${client}.',
                  mapping=dict(client=client.title)), type='info')
        if not errors:
            return self.request.RESPONSE.redirect(self.context.absolute_url())

    def copy_documents(self, client_id):
        transporter = getUtility(ITransporter)
        for doc in self.get_documents():
            transporter.transport_to(doc, client_id, 'eingangskorb')

    def get_documents(self):
        # find documents within the task
        brains = self.context.getFolderContents(
            full_objects=False,
            contentFilter={'portal_type': 'opengever.document.document'})
        for doc in brains:
            yield doc.getObject()
        # find referenced documents
        relatedItems = getattr(self.context, 'relatedItems', None)
        if relatedItems:
            for rel in self.context.relatedItems:
                yield rel.to_object

    def available(self):
        voc = getUtility(IVocabularyFactory,
                         'opengever.task.TargetClientsWithInboxVocabulary')
        if not len(voc(self.context)):
            return False
        elif self.context.task_type_category != 'uni_val':
            return False
        else:
            return True


class CopyRelatedDocumentsToInbox(layout.FormWrapper, grok.View):
    grok.context(Interface)
    grok.name('copy-related-documents-to-inbox')
    grok.require('zope2.View')
    form = CopyRelatedDocumentsForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

    def available(self):
        return self.form_instance.available()
