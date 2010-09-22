from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.utils import get_current_client
from plone.directives import form
from plone.z3cform import layout
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.component import getUtility
import os
import z3c.form
from opengever.ogds.base.interfaces import IContactInformation


class NoItemsSelected(Exception):
    pass

class IChooseDossierSchema(form.Schema):
    """ Form for choosing a target directory
    """

    paths = schema.TextLine(title=u'Selected Items') # hidden
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

            # XXX: implement multiple clients support with additional
            # wizard view
            IStatusMessage(self.request).addStatusMessage(
                'DEBUG NOTICE: No multiple clients support implemented yet!',
                type='warning')

            info = getUtility(IContactInformation)
            home_clients = info.get_assigned_clients()
            # XXX
            client = home_clients[0]

            target = data.get('target_dossier')[1:]
            cid = client.client_id
            trans = getUtility(ITransporter)
            for obj in self.objects:
                trans.transport_to(obj, cid, target)
            redirect_to = os.path.join(client.get('public_url'),
                                       target, '#documents-tab')
            return self.request.RESPONSE.redirect(redirect_to)

    def updateWidgets(self):
        super(CopyDocumentsToRemoteClientForm, self).updateWidgets()
        self.widgets['paths'].mode = HIDDEN_MODE
        self.widgets['paths'].value = ';;'.join(self.item_paths)

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
    grok.name('copy-documents-to-remote-client')
    form = CopyDocumentsToRemoteClientForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.CodeView.__init__(self, *args, **kwargs)

    def __call__(self):
        # XXX: implement multiple clients support with additional
        # wizard view
        IStatusMessage(self.request).addStatusMessage(
            'DEBUG NOTICE: No multiple clients support implemented yet!',
            type='warning')

        info = getUtility(IContactInformation)
        home_clients = info.get_assigned_clients()
        # XXX
        client = home_clients[0]

        home_client_cid = client.client_id
        if get_current_client() == home_client_cid:
            msg = _(u'error_copy_not_supported_at_home_client',
                    default=u'This action is not supported on your home '
                    'client. Use copy and paste.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.RESPONSE.redirect(
                self.request.get('HTTP_REFERER', './') + '#documents-tab')
        else:
            return layout.FormWrapper.__call__(self)
