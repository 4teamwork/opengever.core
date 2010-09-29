from five import grok
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ITransporter
from plone.directives import form
from plone.z3cform import layout
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.component import getUtility
import os
import urllib
import z3c.form


class NoItemsSelected(Exception):
    pass



# ------------------- CHOSE HOME CLIENT ----------------------


class IChooseClientSchema(form.Schema):
    """Schema interface for choosing a sorurce client.
    """

    paths = schema.TextLine(title=u'Selected Items') # hidden
    client = schema.Choice(
        title=_(u'label_source_client',
                default=u'Client'),
        description=_(u'help_source_client',
                      default=u''),
        vocabulary=u'opengever.ogds.base.OtherAssignedClientsVocabulary',
        required=True)


class ChooseClientForm(z3c.form.form.Form):
    fields = z3c.form.field.Fields(IChooseClientSchema)
    label = _(u'title_attach_document_form', u'Attach document')
    ignoreContext = True

    @z3c.form.button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')

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


class ChooseClientView(layout.FormWrapper, grok.CodeView):
    grok.context(IDossierMarker)
    grok.name('copy-documents-to-remote-client')
    form = ChooseClientForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.CodeView.__init__(self, *args, **kwargs)

    __call__ = layout.FormWrapper.__call__




# ------------------- CHOSE DOSSIER --------------------------



class IChooseDossierSchema(IChooseClientSchema):
    """ Form for choosing a target directory
    """

    target_dossier = schema.Choice(
        title = _(u'label_target_dossier', default=u'Target Dossier'),
        description = _(u'help_target_dossier', default=u''),
        vocabulary=u'opengever.ogds.base.HomeDossiersVocabulary',
        required = True,
        )


class CopyDocumentsToRemoteClientForm(z3c.form.form.Form):
    fields = z3c.form.field.Fields(IChooseDossierSchema)
    label = _(u'label_choose_target_dossier', default=u'')
    ignoreContext = True

    @z3c.form.button.buttonAndHandler(_(u'button_copy', default=u'Copy'))
    def handle_copy(self, action):
        data, errors = self.extractData()
        if len(errors)==0:

            info = getUtility(IContactInformation)
            client = info.get_client_by_id(data['client'])

            target = data.get('target_dossier')
            cid = client.client_id
            trans = getUtility(ITransporter)
            for obj in self.objects:
                trans.transport_to(obj, cid, target)
            redirect_to = os.path.join(client.public_url,
                                       target, '#documents')
            return self.request.RESPONSE.redirect(redirect_to)

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
                'path' : {
                    'query' : path,
                    'depth' : 0,
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
        value = self.request.get('paths')
        if not value:
            raise NoItemsSelected
        return value


class CopyDocumentsToRemoteClientView(layout.FormWrapper, grok.CodeView):
    grok.context(IDossierMarker)
    grok.name('copy-documents-to-remote-client2')
    form = CopyDocumentsToRemoteClientForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.CodeView.__init__(self, *args, **kwargs)
