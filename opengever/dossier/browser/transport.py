from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.dexterity.interfaces import IDexterityContent
from five import grok
from opengever.base.interfaces import IRedirector
from opengever.dossier import _
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.utils import get_client_id
from plone.directives import form
from plone.formwidget.autocomplete.widget import AutocompleteSelectionWidget
from plone.z3cform import layout
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import INPUT_MODE
from z3c.form.widget import FieldWidget
from zope import schema
from zope.component import getUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
import os
import urllib
import z3c.form


class NoItemsSelected(Exception):
    pass


class WizardFormMixin(object):
    """Mixing for adding a method witch returns the data needed for rendering
    the wizard steps part. This has nothing to do with the forms itselves, its
    just the steps bar for making it wizard like.
    """

    steps = (
        ('choose_client', _(u'copy_documents_step_choose_client',
                            default=u'1. Choose client')),

        ('choose_dossier', _(u'copy_documents_step_choose_dossier',
                             default=u'2. Choose dossier')))

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


# ------------------- CUSTOM WIDGETS ----------------------
class DossierAutocompleteSelectionWidget(AutocompleteSelectionWidget):
    """Autocomplete widget for selecting a dossier from a client.
    """

    def custom_url_parameters(self):
        info = getUtility(IContactInformation)
        home_clients = tuple(info.get_assigned_clients())

        # is the user assigned to exactly one client?
        if len(home_clients) == 1:
            default = home_clients[0].client_id
        else:
            default = None

        # read the client from the request
        client_id = self.request.get(
            'client', self.request.get('form.widgets.client'),
            default)
        if isinstance(client_id, list) and len(client_id) == 1:
            client_id = client_id[0]

        # it should not be the current client
        if client_id == get_client_id():
            client_id = None

        if client_id:
            # verify that the user is assigned to the requested client
            if client_id not in [client.client_id for client in home_clients]:
                raise RuntimeError(
                    'Expected current user to be assigned to the '
                    'client "%s" read from request' % client_id)

            else:
                return '?client=%s' % client.client_id

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

        return self.js_template % dict(
            id=self.id,
            url=url,
            minLength=self.minLength,
            js_callback=js_callback,
            klass=self.klass,
            title=self.title,
            input_type=self.input_type,
            js_extra=self.js_extra())


@implementer(IFieldWidget)
def DossierAutocompleteFieldWidget(field, request):
    return FieldWidget(field, DossierAutocompleteSelectionWidget(request))


# ------------------- CHOOSE HOME CLIENT ----------------------

class IChooseClientSchema(form.Schema):
    """Schema interface for choosing a sorurce client.
    """

     # hidden
    paths = schema.TextLine(title=u'Selected Items')
    client = schema.Choice(
        title=_(u'label_source_client',
                default=u'Client'),
        description=_(u'help_source_client',
                      default=u''),
        vocabulary=u'opengever.ogds.base.OtherAssignedClientsVocabulary',
        required=True)


class ChooseClientForm(z3c.form.form.Form, WizardFormMixin):
    fields = z3c.form.field.Fields(IChooseClientSchema)
    label = _(u'title_copy_documents_to_dossier',
              default=u'Copy documents to own dossier')
    ignoreContext = True

    template = ViewPageTemplateFile(
        'templates/wizard_wrappedform.pt')
    step_name = 'choose_client'

    @z3c.form.button.buttonAndHandler(_(u'button_continue',
                                        default=u'Continue'))
    def handle_continue(self, action):
        data, errors = self.extractData()
        if not errors:
            data = urllib.urlencode({'form.widgets.client': data['client'],
                                     'form.widgets.paths': data['paths']})
            target = self.context.absolute_url() + \
                '/@@copy-documents-to-remote-client2?' + data
            return self.request.RESPONSE.redirect(target)

    @z3c.form.button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')

    def updateWidgets(self):
        super(ChooseClientForm, self).updateWidgets()
        self.widgets['paths'].mode = HIDDEN_MODE
        self.widgets['paths'].value = ';;'.join(self.item_paths)

    @property
    def item_paths(self):
        field_name = self.prefix + self.widgets.prefix + 'paths'
        value = self.request.get(field_name, False)
        if value:
            value = value.split(';;')
            return value
        value = self.request.get('paths')
        if not value:
            raise NoItemsSelected
        return value


class ChooseClientView(layout.FormWrapper, grok.View):
    grok.context(IDexterityContent)
    grok.name('copy-documents-to-remote-client')
    grok.require('zope2.View')
    form = ChooseClientForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

    def __call__(self):
        factory = getUtility(
            IVocabularyFactory,
            name='opengever.ogds.base.OtherAssignedClientsVocabulary')
        voc = tuple(factory(self.context))

        if not len(voc):
            # if there is no client in the vocabulary we cannot continue
            msg = _(u'warning_copy_to_remote_no_client',
                    default=u'You are not assigned to another client where you'
                    ' could copy the documents to.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        elif len(voc) == 1:
            # we have only one client - selecting this one does not make sense.
            # so we redirect to the next wizard step.
            self.form_instance.update()
            data = urllib.urlencode({
                    'form.widgets.paths': ';;'.join(
                        self.form_instance.item_paths),
                    'form.widgets.client': voc[0].token})

            target = self.context.absolute_url() + \
                '/@@copy-documents-to-remote-client2?' + data
            return self.request.RESPONSE.redirect(target)

        else:
            return layout.FormWrapper.__call__(self)


# ------------------- CHOSE DOSSIER --------------------------

class IChooseDossierSchema(IChooseClientSchema):
    """ Form for choosing a target directory
    """

    target_dossier = schema.Choice(
        title=_(u'label_target_dossier', default=u'Target Dossier'),
        description=_(u'help_target_dossier', default=u''),
        vocabulary=u'opengever.ogds.base.HomeDossiersVocabulary',
        required=True,
        )


class CopyDocumentsToRemoteClientForm(z3c.form.form.Form, WizardFormMixin):
    fields = z3c.form.field.Fields(IChooseDossierSchema)
    fields['target_dossier'].widgetFactory[INPUT_MODE] = \
        DossierAutocompleteFieldWidget
    label = _(u'title_copy_documents_to_dossier',
              default=u'Copy documents to own dossier')
    ignoreContext = True

    template = ViewPageTemplateFile(
        'templates/wizard_wrappedform.pt')
    step_name = 'choose_dossier'

    @z3c.form.button.buttonAndHandler(_(u'button_copy', default=u'Copy'))
    def handle_copy(self, action):
        data, errors = self.extractData()
        if len(errors) == 0:

            info = getUtility(IContactInformation)
            client = info.get_client_by_id(data['client'])

            target = data.get('target_dossier')
            cid = client.client_id
            trans = getUtility(ITransporter)
            for obj in self.objects:
                trans.transport_to(obj, cid, target)
            redirect_to = os.path.join(client.public_url,
                                       target, '#documents')
            redirector = IRedirector(self.request)
            redirector.redirect(redirect_to, target='_blank')
            return self.request.RESPONSE.redirect(
                self.context.absolute_url() + '#documents')

    @z3c.form.button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')

    def updateWidgets(self):
        super(CopyDocumentsToRemoteClientForm, self).updateWidgets()
        self.widgets['paths'].mode = HIDDEN_MODE
        self.widgets['paths'].value = ';;'.join(self.item_paths)
        self.widgets['client'].mode = HIDDEN_MODE

    @property
    def objects(self):
        """ Returns a list of the objects selected in folder contents or
        tabbed view
        """
        catalog = self.context.portal_catalog

        def lookup(path):
            query = {
                'path': {
                    'query': path,
                    'depth': 0,
                    }
                }
            return catalog(query)[0].getObject()
        return [lookup(p) for p in self.item_paths]

    @property
    def item_paths(self):
        field_name = self.prefix + self.widgets.prefix + 'paths'
        value = self.request.get(field_name, False)
        if value:
            value = value.split(';;')
            return value
        value = self.request.get('paths', [])
        return value


class CopyDocumentsToRemoteClientView(layout.FormWrapper, grok.View):
    grok.context(IDexterityContent)
    grok.name('copy-documents-to-remote-client2')
    grok.require('zope2.View')
    form = CopyDocumentsToRemoteClientForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)
