"""
The transporter module defines functionality for adding a document
from any context of a foreign client into a existing task.
"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ITransporter
from opengever.task import _
from opengever.task.task import ITask
from plone.directives import form
from plone.z3cform import layout
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import urllib
import z3c.form
from plone.formwidget.autocomplete.widget import AutocompleteFieldWidget
from z3c.form.interfaces import INPUT_MODE


class NoItemsSelected(Exception):
    pass


class WizardFormMixin(object):
    """Mixing for adding a method witch returns the data needed for rendering
    the wizard steps part. This has nothing to do with the forms itselves, its
    just the steps bar for making it wizard like.
    """

    steps = (
        ('choose_client', _(u'attachdocument_step_choose_client',
                            default=u'1. Choose client')),

        ('choose_dossier', _(u'attachdocument_step_choose_dossier',
                             default=u'2. Choose dossier')),

        ('choose_document', _(u'attachdocument_step_choose_document',
                              default=u'3. Choose document')))

    def wizard_steps(self):
        """Return ordered list of wizards.
        """

        current_reached = False

        for name, label in self.steps:
            classes = ['wizard-step-%s' % name]
            if name == self.step_name:
                current_reached = True
                classes.append('selected')
            elif not current_reached:
                classes.append('visited')
            yield {'name': name,
                   'label': label,
                   'class': ' '.join(classes)}




# ------------------- CHOSE HOME CLIENT ----------------------


class IChooseClientSchema(form.Schema):
    """Schema interface for choosing a sorurce client.
    """

    client = schema.Choice(
        title=_(u'label_source_client',
                default=u'Client'),
        description=_(u'help_source_client',
                      default=u''),
        vocabulary=u'opengever.ogds.base.OtherAssignedClientsVocabulary',
        required=True)


class ChooseClientForm(z3c.form.form.Form, WizardFormMixin):
    fields = z3c.form.field.Fields(IChooseClientSchema)
    label = _(u'title_attach_document_form', u'Attach document')
    ignoreContext = True
    template = ViewPageTemplateFile(
        'attachdocument_templates/wizard_wrappedform.pt')
    step_name = 'choose_client'

    @z3c.form.button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')

    @z3c.form.button.buttonAndHandler(_(u'button_continue',
                                        default=u'Continue'))
    def handle_continue(self, action):
        data, errors = self.extractData()
        if not errors:
            data = urllib.urlencode({'form.widgets.client': data['client']})
            target = self.context.absolute_url() + \
                '/@@choose_source_dossier?' + data
            return self.request.RESPONSE.redirect(target)


class ChooseClientView(layout.FormWrapper, grok.CodeView):
    grok.context(ITask)
    grok.name('choose_source_client')
    form = ChooseClientForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.CodeView.__init__(self, *args, **kwargs)

    def __call__(self):
        factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.OtherAssignedClientsVocabulary')
        if not len(factory(self.context)):
            # if there is no client in the vocabulary we cannot continue
            msg = _(u'warning_attach_document_no_other_home_client',
                    default=u'You are not assigned to another home client '
                    'from where you could copy a document.')
            IStatusMessage(self.request).addStatusMessage(msg, type='warning')
            return self.request.RESPONSE.redirect(self.context.absolute_url())
        else:
            return layout.FormWrapper.__call__(self)




# ------------------- CHOSE DOSSIER --------------------------

class IChooseDossierSchema(IChooseClientSchema):
    """ Form for choosing a source dossier on my home client
    """

    source_dossier = schema.Choice(
        title=_(u'label_source_dossier', default=u'Dossier'),
        description=_(u'help_source_dossier',
                      default=u'Select a source dossier'),
        vocabulary=u'opengever.ogds.base.HomeDossiersVocabulary',
        required=True,
        )


class ChooseDossierForm(z3c.form.form.Form, WizardFormMixin):
    fields = z3c.form.field.Fields(IChooseDossierSchema)
    # fields['source_dossier'].widgetFactory[INPUT_MODE] = AutocompleteFieldWidget

    label = _(u'title_attach_document_form', u'Attach document')
    ignoreContext = True

    template = ViewPageTemplateFile(
        'attachdocument_templates/wizard_wrappedform.pt')
    step_name = 'choose_dossier'

    def updateWidgets(self):
        super(ChooseDossierForm, self).updateWidgets()
        self.widgets['client'].mode = HIDDEN_MODE

    @z3c.form.button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')

    @z3c.form.button.buttonAndHandler(_(u'button_continue',
                                        default=u'Continue'))
    def handle_continue(self, action):
        data, errors = self.extractData()
        if not errors:
            data = urllib.urlencode({'form.widgets.client': data['client'],
                                     'form.widgets.source_dossier':
                                         data['source_dossier']})
            target = self.context.absolute_url() + \
                '/@@choose_source_document?' + data
            return self.request.RESPONSE.redirect(target)


class ChooseDossierView(layout.FormWrapper, grok.CodeView):
    grok.context(ITask)
    grok.name('choose_source_dossier')
    form = ChooseDossierForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.CodeView.__init__(self, *args, **kwargs)

    __call__ = layout.FormWrapper.__call__



# ------------------- CHOSE DOCUMENT --------------------------


class IChooseDocumentSchema(IChooseDossierSchema):
    """ Select a document from the previously selected dossier
    """

    source_document = schema.Choice(
        title=_(u'label_source_document', default=u'Document'),
        description=_(u'help_source_document', default=u'Select a document'),
        vocabulary=u'opengever.ogds.base.DocumentInSelectedDossierVocabulary',
        required=True,
        )



class ChooseDocumentForm(z3c.form.form.Form, WizardFormMixin):
    fields = z3c.form.field.Fields(IChooseDocumentSchema)
    # fields['source_document'].widgetFactory[INPUT_MODE] = AutocompleteFieldWidget

    label = _(u'title_attach_document_form', u'Attach document')
    ignoreContext = True

    template = ViewPageTemplateFile(
        'attachdocument_templates/wizard_wrappedform.pt')
    step_name = 'choose_document'

    def updateWidgets(self):
        super(ChooseDocumentForm, self).updateWidgets()
        self.widgets['client'].mode = HIDDEN_MODE
        self.widgets['source_dossier'].mode = HIDDEN_MODE

    @z3c.form.button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')

    @z3c.form.button.buttonAndHandler(_(u'button_attach', default=u'Attach'))
    def handle_attach(self, action):
        data, errors = self.extractData()
        if not errors:
            document = data.get('source_document')
            info = getUtility(IContactInformation)

            client = info.get_client_by_id(data['client'])
            home_clients = info.get_assigned_clients()

            if client not in home_clients:
                raise ValueError('Expected %s to be a ' % data['client'] + \
                                     'assigned client of the current user.')

            cid = client.client_id

            trans = getUtility(ITransporter)
            trans.transport_from(self.context, cid, document)
            url = self.context.absolute_url()
            return self.request.RESPONSE.redirect(url)



class ChooseDocumentView(layout.FormWrapper, grok.CodeView):
    grok.context(ITask)
    grok.name('choose_source_document')
    form = ChooseDocumentForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.CodeView.__init__(self, *args, **kwargs)

    __call__ = layout.FormWrapper.__call__


