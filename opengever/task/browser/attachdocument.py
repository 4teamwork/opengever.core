"""
The transporter module defines functionality for adding a document
from any context of a foreign client into a existing task.
"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from five import grok
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.utils import get_client_id
from opengever.task import _
from opengever.task.task import ITask
from plone.directives import form
from plone.z3cform import layout
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import INPUT_MODE
from z3c.form.widget import FieldWidget
from zope import schema
from zope.component import getUtility
from zope.interface import implementer, Interface
import urllib
import z3c.form


# ------------------- CONTROLLER --------------------------

class AttachDocumentAllowed(grok.View):
    """This controller view checks if the "attach document" action should
    be available for this user on this context.

    Only display the action if the user is assigned to at least one *other*
    client.
    """

    grok.context(Interface)
    grok.name('attach-document-allowed')
    grok.require('zope2.View')

    def render(self):
        info = getUtility(IContactInformation)
        clients = filter(lambda client: client.client_id != get_client_id(),
                         info.get_assigned_clients())
        return len(clients) > 0


# ------------------- WIZARD --------------------------

class WizardFormMixin(object):
    """Mixing for adding a method witch returns the data needed for rendering
    the wizard steps part. This has nothing to do with the forms itselves, its
    just the steps bar for making it wizard like.
    """

    steps = (
        ('choose_dossier', _(u'attachdocument_step_choose_dossier',
                             default=u'1. Choose dossier')),

        ('choose_document', _(u'attachdocument_step_choose_document',
                              default=u'2. Choose document')))

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

    def set_client_id(self, task):
        """Sets the client id in the request for making the dossier / document
        vocabularies work.
        """

        task.REQUEST.set('client', task.responsible_client)


# ------------------- SPECIAL AUTOCOMPLETE WIDGET --------------------------

from plone.formwidget.autocomplete.widget import AutocompleteSelectionWidget


class ExtendedAutocompleteSelectionWidget(AutocompleteSelectionWidget):
    """Make it possible to add custom url parameters to the source url.
    """

    def custom_url_parameters(self):
        return ''

    def js(self):

        form_url = self.request.getURL()

        form_prefix = self.form.prefix + self.__parent__.prefix
        widget_name = self.name[len(form_prefix):]

        url = "%s/++widget++%s/@@autocomplete-search%s" % (
            form_url, widget_name, self.custom_url_parameters())

        js_callback = self.js_callback_template % dict(
            id=self.id,
            name=self.name,
            klass=self.klass,
            title=self.title,
            termCount=len(self.terms))

        return self.js_template % dict(id=self.id,
                                       url=url,
                                       minLength=self.minLength,
                                       js_callback=js_callback,
                                       klass=self.klass,
                                       title=self.title,
                                       input_type=self.input_type,
                                       js_extra=self.js_extra())


class DossierAutocompleteSelectionWidget(ExtendedAutocompleteSelectionWidget):
    """Autocomplete widget for selecting a dossier from a specific client.
    """

    def custom_url_parameters(self):
        # to which clients is the user assigned?
        info = getUtility(IContactInformation)
        clients = info.get_assigned_clients()
        client_ids = [client.client_id for client in clients]

        # is the responsible client of the task one of the users assigned
        # tasks? it should be!
        if self.context.responsible_client not in client_ids:
            return ''
        else:
            return '?client=%s' % self.context.responsible_client


@implementer(IFieldWidget)
def DossierAutocompleteFieldWidget(field, request):
    return FieldWidget(field, DossierAutocompleteSelectionWidget(request))


class DocumentAutocompleteSelectionWidget(DossierAutocompleteSelectionWidget):
    """Autocomplete widget for selecting a document from a dossier
    within a specific client.
    """

    def custom_url_parameters(self):
        params = super(DocumentAutocompleteSelectionWidget,
                       self).custom_url_parameters()
        if not params:
            return ''
        else:
            dossier = self.context.REQUEST.get('form.widgets.source_dossier')
            return '%s&dossier_path=%s' % (params, dossier)


@implementer(IFieldWidget)
def DocumentAutocompleteFieldWidget(field, request):
    return FieldWidget(field, DocumentAutocompleteSelectionWidget(request))


# ------------------- CHOSE DOSSIER --------------------------

class IChooseDossierSchema(form.Schema):
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
    fields['source_dossier'].widgetFactory[INPUT_MODE] = \
        DossierAutocompleteFieldWidget

    label = _(u'title_attach_document_form', u'Attach document')
    ignoreContext = True

    template = ViewPageTemplateFile(
        'templates/wizard_wrappedform.pt')
    step_name = 'choose_dossier'

    @z3c.form.button.buttonAndHandler(_(u'button_continue',
                                        default=u'Continue'))
    def handle_continue(self, action):
        data, errors = self.extractData()
        if not errors:
            data = urllib.urlencode({'form.widgets.source_dossier':
                                         data['source_dossier']})
            target = self.context.absolute_url() + \
                '/@@choose_source_document?' + data
            return self.request.RESPONSE.redirect(target)

    @z3c.form.button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')

    def update(self):
        self.request.set('client', self.context.responsible_client)
        super(ChooseDossierForm, self).update()


class ChooseDossierView(layout.FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('choose_source_dossier')
    grok.require('cmf.AddPortalContent')
    form = ChooseDossierForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

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
    fields['source_document'].widgetFactory[INPUT_MODE] = \
        DocumentAutocompleteFieldWidget

    label = _(u'title_attach_document_form', u'Attach document')
    ignoreContext = True

    template = ViewPageTemplateFile(
        'templates/wizard_wrappedform.pt')
    step_name = 'choose_document'

    @z3c.form.button.buttonAndHandler(_(u'button_attach', default=u'Attach'))
    def handle_attach(self, action):
        data, errors = self.extractData()
        if not errors:
            document = data.get('source_document')
            info = getUtility(IContactInformation)

            client = info.get_client_by_id(self.request.get('client'))
            home_clients = info.get_assigned_clients()

            if client not in home_clients:
                raise ValueError('Expected %s to be a assigned client '
                                 'of the current user.' % data['client'])

            cid = client.client_id

            trans = getUtility(ITransporter)
            trans.transport_from(self.context, cid, document)

            url = self.context.absolute_url()
            return self.request.RESPONSE.redirect(url)

    @z3c.form.button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')

    def update(self):
        self.request.set('client', self.context.responsible_client)
        return super(ChooseDocumentForm, self).update()

    def updateWidgets(self):
        super(ChooseDocumentForm, self).updateWidgets()
        self.widgets['source_dossier'].mode = HIDDEN_MODE


class ChooseDocumentView(layout.FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('choose_source_document')
    grok.require('cmf.AddPortalContent')
    form = ChooseDocumentForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

    __call__ = layout.FormWrapper.__call__
