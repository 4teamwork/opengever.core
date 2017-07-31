from opengever.ech0147 import _
from opengever.ech0147.bindings import ech0147t1
from opengever.ech0147.interfaces import IECH0147Settings
from opengever.ech0147.utils import create_dossier
from plone.namedfile import field as namedfile
from plone.registry.interfaces import IRegistry
from z3c.form import form, field, button
from zExceptions import NotFound
from zipfile import ZipFile
from zope.component import getUtility
from zope.interface import Interface


class IECH0147ImportFormSchema(Interface):

    message = namedfile.NamedBlobFile(
        title=_(u'label_message', default=u'Message'),
        description=_(u'help_message', default=u''),
        required=True,
        )


class ECH0147ImportForm(form.Form):
    fields = field.Fields(IECH0147ImportFormSchema)
    ignoreContext = True  # don't use context to get widget data
    label = _(u'label_ech0147_import_form', u'eCH 0147 Import')

    @button.buttonAndHandler(_(u'label_import', default=u'Import'))
    def handleSave(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return

        with ZipFile(data['message'].open(), 'r') as zipfile:
            try:
                zipinfo = zipfile.getinfo('message.xml')
            except KeyError:
                self.status = _(u'Invalid message. Missing message.xml')
                return

            xml = zipfile.read(zipinfo)

            message = ech0147t1.CreateFromDocument(xml)
            if message.content_.documents and message.content_.dossiers:
                self.status = _(u'Messages containing toplevel dossiers and '
                                'toplevel documents are not supported')
                return

            if message.content_.dossiers:
                for dossier in message.content_.dossiers.dossier:
                    create_dossier(self.context, dossier, zipfile)

        self.status = _(u"Message has been imported")
        return self.render()

    @button.buttonAndHandler(_(u'label_cancel', default=u'Cancel'))
    def handleCancel(self, action):
        self.request.response.redirect(self.context.absolute_url())

    def updateWidgets(self):
        super(ECH0147ImportForm, self).updateWidgets()
        self.widgets['message'].value = None

    def render(self):
        if not self.enabled():
            raise NotFound()
        return super(ECH0147ImportForm, self).render()

    def enabled(self):
        registry = getUtility(IRegistry)
        ech0147_settings = registry.forInterface(IECH0147Settings, check=False)
        return ech0147_settings.ech0147_import_enabled
