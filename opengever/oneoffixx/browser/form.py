from opengever.oneoffixx import _
from opengever.oneoffixx.command import CreateDocumentFromOneOffixxTemplateCommand
from plone.supermodel import model
from plone.z3cform.layout import FormWrapper
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.form import Form
from zope import schema


class ICreateDocumentFromOneOffixxTemplate(model.Schema):

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True)


class SelectOneOffixxTemplateDocumentWizardStep(Form):

    label = _(u'create_document_with_template', default=u'Create document from template')
    ignoreContext = True
    fields = Fields(ICreateDocumentFromOneOffixxTemplate)

    def finish_document_creation(self, data):
        new_doc = self.create_document(data)
        self.activate_external_editing(new_doc)
        return self.request.RESPONSE.redirect(new_doc.absolute_url())

    def activate_external_editing(self, new_doc):
        """Add the oneoffixx external_editor URL to redirector queue."""
        new_doc.setup_external_edit_redirect(self.request, action="oneoffixx")

    def create_document(self, data):
        """Create a new document based on a template."""
        command = CreateDocumentFromOneOffixxTemplateCommand(self.context, data['title'])
        return command.execute()

    @button.buttonAndHandler(_('button_save', default=u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()

        if not errors:
            return self.finish_document_creation(data)

        self.status = self.formErrorsMessage
        return None

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


class SelectOneOffixxTemplateDocumentView(FormWrapper):

    form = SelectOneOffixxTemplateDocumentWizardStep
