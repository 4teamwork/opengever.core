from datetime import datetime
import re

from five import grok
from zope import component
from zope.interface import Interface
from zope import schema
from zope.schema import vocabulary
from z3c.form import form, field, button

from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.dexterity.interfaces import IDexterityContent
from plone.z3cform import layout

from opengever.dossier.behaviors.dossier import IDossier
from opengever.document.document import IDocumentSchema
from opengever.document import _


DOCUCOMPOSER_TEMPLATES = {
    '2798' : 'Aktennotiz',
    '1159' : 'Bericht A4',
    '1150' : 'Einladung',
    '3541' : 'Checklisten',
    }
DOCUCOMPOSER_TEMPLATES_VOCABULARY = vocabulary.SimpleVocabulary([
        vocabulary.SimpleTerm(k, title=v)
        for k, v
        in DOCUCOMPOSER_TEMPLATES.items()
        ])

class IDocuComposerWizard(Interface):
    template = schema.Choice(
        title = _(u'label_docucomposer_wizard', default=u'DocuComposer Template'),
        description = _(u'help_docucomposer_wizard', default=u''),
        vocabulary = DOCUCOMPOSER_TEMPLATES_VOCABULARY,
        required = True
        )
    filename = schema.TextLine(
        title = _(u'lable_docucomposer_filename', default=u'Filename'),
        description = _(u'help_docucomposer_filename', default=u''),
        required = True,
        )



class DocuComposerWizardForm(form.Form):
    fields = field.Fields(IDocuComposerWizard)
    ignoreContext = True
    label = _(u'heading_docucomposer_wizard_form', default=u'DocuComposer')

    @button.buttonAndHandler(_(u'button_create', default='Create'))
    def create_button_handler(self, action):
        data, errors = self.extractData()
        if len(errors)==0:
            current_user = str(self.context.portal_membership.getAuthenticatedMember())
            filename = data['filename']
            if not filename.endswith('.doc'):
                filename += '.doc'
            filename = component.getUtility(IIDNormalizer).normalize(filename)
            url = 'docucomposer:url=%s&id=%s&filename=%s&owner=%s' % (
                self.context.absolute_url(),
                data['template'],
                filename,
                current_user,
                )
            return self.request.RESPONSE.redirect(url)



class DocuComposerWizardView(layout.FormWrapper, grok.CodeView):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('docucomposer-wizard')
    form = DocuComposerWizardForm

    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.CodeView.__init__(self, context, request)

    def render(self):
        return layout.FormWrapper.__call__(self)



class CreateDocumentWithFile(grok.CodeView):
    grok.context(IDexterityContent)
    grok.name("create_document_with_file")
    grok.require("zope2.View")

    def render(self):

        title = self.request.get('title')
        uploadFile = self.request.get('file')
        filename = self.request.get('fileName')
        current_user = self.request.get('userid')


        #current_user = str(context.portal_membership.getAuthenticatedMember())
        self.context.plone_utils.changeOwnershipOf(self.context, current_user)

        generated_id = component.getUtility(IIDNormalizer).normalize(title)
        id = generated_id
        counter = 1
        while 1:
            if self.context.get(id):
                id = generated_id + '-' + str(counter)
                counter += 1
            else:
                break

        obj = self.context.get(self.context.invokeFactory(type_name="opengever.document.document", id=id, title=title))

        fields = dict(getFieldsInOrder(IDocumentSchema))
        fileObj = fields['file']._type(data=uploadFile, filename=filename)
        obj.file = fileObj
        obj.document_date = datetime.now()

        portal = self.context.portal_url.getPortalObject()
        xpr = re.compile('href="(.*?)"')
        html = portal.externalEditLink_(obj)
        url = xpr.search(html).groups()[0]
        return url
