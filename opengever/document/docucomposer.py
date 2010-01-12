from zope.interface import Interface
from zope import schema
from zope.schema import vocabulary

from AccessControl import SecurityManagement
from five import grok
from DateTime import DateTime
from z3c.form import form, field, button, interfaces

from persistent.dict import PersistentDict
from plone.z3cform import layout
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.browser.base import DexterityExtensibleForm

from opengever.document import _
from opengever.document.persistence import DCQueue
from opengever.document.document import IDocumentSchema

DOCUCOMPOSER_TEMPLATES = {
    '2798': 'Aktennotiz',
    '1159': 'Bericht A4',
    '1150': 'Einladung',
    '3541': 'Checklisten',
    }
DOCUCOMPOSER_TEMPLATES_VOCABULARY = vocabulary.SimpleVocabulary([
        vocabulary.SimpleTerm(k, title=v)
        for k, v
        in DOCUCOMPOSER_TEMPLATES.items()])


class DocuComposerWizardForm(DexterityExtensibleForm, form.AddForm):
    portal_type='opengever.document.document'
    ignoreContext = True
    label = _(u'heading_docucomposer_wizard_form', default=u'DocuComposer')
    
    def updateWidgets(self, *args, **kwargs):
        import pdb; pdb.set_trace( )
        super(DocuComposerWizardForm, self).updateWidgets(*args, **kwargs)
        filefields = filter(lambda a:not not a, [g.fields.get('file', None) for g in self.groups])
        if len(filefields)>0:
            filefields[0].mode = interfaces.HIDDEN_MODE
        # fil = self.schema['file']
        # fil.readonly = True

    @button.buttonAndHandler(_(u'button_create', default='Create'))
    def create_button_handler(self, action):
        data, errors = self.extractData()
        if len(errors)==0:
            data.__setitem__('owner', self.context.portal_membership.getAuthenticatedMember())
            data.__setitem__('context', self.context)
            data.__setitem__('creation_date', DateTime())
            queue = DCQueue(self.context)
            persData = PersistentDict(data)
            token = queue.appendDCDoc(persData)

            url = 'docucomposer:url=%s&token=%s' % (
                self.context.portal_url(),
                token,
            )
            print token
            print url

            queue.clearUp()

            return self.request.RESPONSE.redirect(url)


class DocuComposerWizardView(layout.FormWrapper, grok.CodeView):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('docucomposer-wizard')
    form = DocuComposerWizardForm
    
    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.CodeView.__init__(self, context, request)


class CreateDocumentWithFile(grok.CodeView):
    from Products.CMFPlone.interfaces import IPloneSiteRoot
    grok.context(IPloneSiteRoot)
    grok.name("create_document_with_file")
    grok.require("zope2.View")

    def render(self):
        token = self.request.get('token')
        uploadFile = self.request.get('file')
        filename = self.request.get('filename')

        queue = DCQueue(self.context)
        dcDict = queue.getDCDocs()
        data = dcDict.get(token, dcDict)

        if data:
            data = data.data
            user = data['owner']
            SecurityManagement.newSecurityManager(self.request, user)

            dossier = data['context']

            new_doc = createContentInContainer(dossier, 'opengever.document.document', title= data['title'])
            new_doc.REQUEST = self.context.REQUEST

            for key in data.keys():
                new_doc.__setattr__(key, data[key])

            fields = dict(schema.getFieldsInOrder(IDocumentSchema))
            fileObj = fields['file']._type(data=uploadFile, filename=filename)
            new_doc.file = fileObj

            url = new_doc.absolute_url()

            return url
