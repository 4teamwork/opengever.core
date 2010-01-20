from zope.interface import Interface
from zope import schema
from zope.schema import vocabulary
from zope.app.intid.interfaces import IIntIds

from zope.component import getUtility

from AccessControl import SecurityManagement
from five import grok
from DateTime import DateTime
from z3c.form import form, button, interfaces

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
        super(DocuComposerWizardForm, self).updateWidgets(*args, **kwargs)
        filefields = filter(lambda a:not not a, [g.fields.get('file', None) for g in self.groups])
        if len(filefields)>0:
            filefields[0].mode = interfaces.HIDDEN_MODE

    @button.buttonAndHandler(_(u'button_create', default='Create'))
    def create_button_handler(self, action):
        data, errors = self.extractData()
        if len(errors)==0:
            data['owner'] = self.context.portal_membership.getAuthenticatedMember().getId()
            intids = getUtility( IIntIds )
            data['intid'] = intids.getId( self.context )
            data['creation_date'] = DateTime()
            queue = DCQueue(self.context)
            token = queue.appendDCDoc(data)

            print token
            
            queue.clearUp()
            
            return self.request.RESPONSE.redirect('docucomposer-start?token=%s' % token)
            

class DocuComposerWizardView(layout.FormWrapper, grok.CodeView):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('docucomposer-wizard')
    form = DocuComposerWizardForm
    
    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.CodeView.__init__(self, context, request)


class StartDCLauncher(grok.CodeView):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('docucomposer-start')
    
    def url(self):
        if self.request.get('token'):
            url = 'docucomposer:url=%s&token=%s' % (
                self.context.portal_url(),
                self.request.get('token'),
            )
            return url
        return None

    
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
            userid = data['owner']
            
            uf = self.context.acl_users
            user = uf.getUserById(userid)
            if not hasattr(user, 'aq_base'):
                user = user.__of__(uf)
            SecurityManagement.newSecurityManager(self.request, user)

            intids = getUtility( IIntIds )

            dossier = intids.getObject(data['intid'])

            #remove unused attributes in the data dict
            data.pop('owner')
            data.pop('intid')

            new_doc = createContentInContainer(dossier, 'opengever.document.document', **data)

            fields = dict(schema.getFieldsInOrder(IDocumentSchema))
            fileObj = fields['file']._type(data=uploadFile, filename=filename)
            new_doc.file = fileObj

            # Fix:  we get again the document, because the request of the return from createContentInContainer are wrong
            doc = self.context.restrictedTraverse('/'.join(new_doc.getPhysicalPath()))
            url = doc.absolute_url()

            #remove 
            queue.removeDCDoc(token)
            
            return url
