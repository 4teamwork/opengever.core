from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.ech0147 import _
from opengever.ech0147.bindings import ech0147t1
from opengever.ech0147.interfaces import IECH0147Settings
from opengever.ech0147.utils import create_document
from opengever.ech0147.utils import create_dossier
from opengever.ogds.base.sources import AllUsersSourceBinder
from opengever.ogds.models.service import ogds_service
from opengever.repository.interfaces import IRepositoryFolder
from plone.autoform import directives
from plone.autoform.form import AutoExtensibleForm
from plone.namedfile import field as namedfile
from plone.registry.interfaces import IRegistry
from plone.supermodel.model import Schema
from Products.statusmessages.interfaces import IStatusMessage
from pyxb import UnrecognizedContentError
from z3c.form import form, button
from z3c.form.interfaces import IErrorViewSnippet
from zExceptions import BadRequest
from zExceptions import NotFound
from zipfile import ZipFile
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.pagetemplate.interfaces import IPageTemplate
import transaction


class IECH0147ImportFormSchema(Schema):

    message = namedfile.NamedBlobFile(
        title=_(u'label_message', default=u'File'),
        description=_(
            u'help_message',
            default=u'A ZIP file containing an eCH-147 message.'),
        required=True,
        )

    directives.widget('responsible', KeywordFieldWidget, async=True)
    responsible = schema.Choice(
        title=_(u'label_reponsible', default=u'Responsible'),
        description=_(u'help_responsible',
                      default=u'Responsible for dossiers created by eCH-0147 '
                      'import.'),
        source=AllUsersSourceBinder(),
        required=True,
    )


@implementer(IErrorViewSnippet)
class ErrorViewSnippet(object):

    def __init__(self, error, request, widget):
        self.error = error
        self.request = request
        self.widget = widget
        self.message = error
        self.context = None

    def update(self):
        pass

    def render(self):
        template = getMultiAdapter(
            (self, self.request), IPageTemplate)
        return template(self)


class ECH0147ImportForm(AutoExtensibleForm, form.Form):
    schema = IECH0147ImportFormSchema
    ignoreContext = True  # don't use context to get widget data
    label = _(u'label_ech0147_import_form', u'eCH 0147 Import')
    import_successful = False

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
                self.set_form_error(
                    _(u'Invalid message. Missing message.xml'),
                    self.widgets['message'])
                return

            xml = zipfile.read(zipinfo)

            try:
                message = ech0147t1.CreateFromDocument(xml)
            except UnrecognizedContentError as e:
                self.set_form_error(
                    _(u'msg_ech0147_invalid_content',
                        default=u'Invalid content. ${details}',
                        mapping={'details': e.details()}),
                    self.widgets['message'])
                return

            if IRepositoryFolder.providedBy(self.context) \
               and message.content_.documents:
                self.set_form_error(
                    _(u'This message contains toplevel documents. '
                      'It can only be imported within a dossier.'),
                    self.widgets['message'])
                return

            if message.content_.documents:
                for document in message.content_.documents.document:
                    try:
                        create_document(self.context, document, zipfile)
                    except BadRequest as exc:
                        return self._import_error(document, exc)

            if message.content_.dossiers:
                for dossier in message.content_.dossiers.dossier:
                    try:
                        create_dossier(
                            self.context, dossier, zipfile,
                            data['responsible'])
                    except BadRequest as exc:
                        return self._import_error(dossier, exc)

        self.import_successful = True

    @button.buttonAndHandler(_(u'label_cancel', default=u'Cancel'))
    def handleCancel(self, action):
        self.request.response.redirect(self.context.absolute_url())

    def updateActions(self):
        super(ECH0147ImportForm, self).updateActions()
        self.actions['label_import'].addClass("context")

    def updateWidgets(self):
        super(ECH0147ImportForm, self).updateWidgets()
        self.widgets['message'].value = None

        # Set default responsible to current user
        if not self.request.form.get('form.widgets.responsible'):
            user = ogds_service().fetch_current_user()
            if user is not None:
                self.widgets['responsible'].value = [user.userid]
                self.widgets['responsible'].update()

    def update(self):
        self.request.set('disable_border', 1)
        return super(ECH0147ImportForm, self).update()

    def render(self):
        if not self.enabled():
            raise NotFound()
        if self.import_successful:
            IStatusMessage(self.request).addStatusMessage(
                _(u"Message has been imported"), type='info')
            self.request.response.redirect(self.context.absolute_url())
        return super(ECH0147ImportForm, self).render()

    def available(self):
        if not self.enabled():
            return False
        if IDossierMarker.providedBy(self.context):
            return True
        if not IRepositoryFolder.providedBy(self.context):
            return False
        if self.context.is_leaf_node():
            return True
        return False

    def enabled(self):
        registry = getUtility(IRegistry)
        ech0147_settings = registry.forInterface(IECH0147Settings, check=False)
        return ech0147_settings.ech0147_import_enabled

    def set_form_error(self, error, widget):
        self.status = self.formErrorsMessage
        view = ErrorViewSnippet(error, self.request, widget)
        widget.error = view
        self.widgets.errors = (view,)

    def _import_error(self, item, exc):
        transaction.abort()

        errors = []
        for error in exc.message:
            msg = u'{} `{}`: {}'.format(
                translate(_(u'label_field', default=u'Field'), context=self.request),
                error['field'],
                translate(error['message'], domain='plone', context=self.request))
            errors.append(msg)

        self.rendered_error_message = _(
            u"Message import failed. The object ${title} has invalid "
            "field data. <br /> ${details}",
            mapping={'title': item.titles.title[0].value(),
                     'details': u'<br />'.join(errors)})

        return
