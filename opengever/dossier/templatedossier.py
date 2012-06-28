from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from ftw.table import helper
from ftw.table.interfaces import ITableGenerator
from opengever.base.interfaces import IRedirector
from opengever.dossier import _
from opengever.tabbedview.browser.tabs import Documents, Trash
from opengever.tabbedview.helper import linked
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import iterSchemata
from plone.rfc822.interfaces import IPrimaryField
from z3c.form.interfaces import IValue
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFieldsInOrder


REMOVED_COLUMNS = ['receipt_date', 'delivery_date', 'containing_subdossier']
NO_DEFAULT_VALUE_FIELDS = ['title', 'file']


class ITemplateDossier(Interface):
    pass


class ITemplateUtility(Interface):
    pass


class TemplateDocumentFormView(grok.View):
    """ Show the "Document with Tempalte"-Form
        A Form wich show all static templates.
    """

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('document_with_template')
    grok.template('template_form')
    label = _('create_document_with_template',
        default="create document with template")

    def __call__(self):

        self.errors = {}
        self.title = ''
        self.edit = False

        if self.request.get('form.buttons.save'):

            #inialize attributes with the values from the request.
            path = None
            if self.request.get('paths'):
                path = self.request.get('paths')[0]
            self.title = self.request.get('title', '').decode('utf8')
            self.edit = self.request.get('form.widgets.edit_form') == ['on']

            if path and self.title:
                #create document
                newdoc = self.create_document(path)

                # check if the direct-edit-mode is selected
                if self.edit:
                    self.activate_external_editing(newdoc)

                return self.request.RESPONSE.redirect(
                        self.context.absolute_url() + '#documents')

            else:
                if path is None:
                    self.errors['paths'] = True
                if not self.title:
                    self.errors['title'] = True

        elif self.request.get('form.buttons.cancel'):
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        return self.render_form()

    def activate_external_editing(self, newdoc):
        """Checkout the given document, and add the external_editor url
        to redirector cue"""

        # checkout the document
        manager = self.context.restrictedTraverse(
            'checkout_documents')
        manager.checkout(newdoc)

        # Add redirect to the zem-file download,
        # for starting external editing with external editor.

        redirector = IRedirector(self.request)
        redirector.redirect(
            '%s/external_edit' % newdoc.absolute_url(),
            target='_self',
            timeout=1000)

    def create_document(self, path):
        doc = self.context.restrictedTraverse(path)
        _type = self._get_primary_field_type(doc)

        new_file = _type(data=doc.file.data,
                         filename=doc.file.filename)

        new_doc = createContentInContainer(
            self.context, 'opengever.document.document',
            title=self.title, file=new_file)

        self._set_defaults(new_doc)
        # notify necassary standard events
        notify(ObjectModifiedEvent(new_doc))

        return new_doc

    def _get_primary_field_type(self, obj):

        for schemata in iterSchemata(obj):
            for name, field in getFieldsInOrder(schemata):
                if IPrimaryField.providedBy(field):
                    return field._type

    def _set_defaults(self, obj):
        # set default values for all fields

        for schemata in iterSchemata(obj):
            for name, field in getFieldsInOrder(schemata):
                if name not in NO_DEFAULT_VALUE_FIELDS:
                    default = queryMultiAdapter((
                            obj,
                            obj.REQUEST,
                            None,
                            field,
                            None,
                            ), IValue, name='default')
                    if default is not None:
                        default = default.get()
                    if default is None:
                        default = getattr(field, 'default', None)
                    if default is None:
                        try:
                            default = field.missing_value
                        except AttributeError:
                            pass
                    value = default
                    field.set(field.interface(obj), value)

    def render_form(self):
        # get the templatedocuments and show the form template
        templateUtil = getUtility(
            ITemplateUtility, 'opengever.templatedossier')
        self.templatedossier = templateUtil.templateFolder(self.context)
        if self.templatedossier is None:
            status = IStatusMessage(self.request)
            status.addStatusMessage(
                _("Not found the templatedossier"), type="error")
            return self.context.request.RESPONSE.redirect(
                self.context.absolute_url())
        return super(
            TemplateDocumentFormView, self).__call__()

    def templates(self):
        generator = getUtility(ITableGenerator, 'ftw.tablegenerator')
        catalog = getToolByName(self.context, 'portal_catalog')
        templates = catalog(
            path=dict(
                depth=1, query=self.templatedossier),
            portal_type="opengever.document.document")
        generator = getUtility(ITableGenerator, 'ftw.tablegenerator')

        columns = (
            (''),
            ('', helper.path_radiobutton),
            {'column': 'Title',
             'column_title': _(u'label_title', default=u'title'),
             'sort_index': 'sortable_title',
             'transform': linked},
            {'column': 'Creator',
             'column_title': _(u'label_creator', default=u'Creator'),
             'sort_index': 'document_author'},
            {'column': 'modified',
             'column_title': _(u'label_modified', default=u'Modified'),
             'transform': helper.readable_date}
            )
        return generator.generate(templates, columns)


class TemplateFolder(grok.GlobalUtility):
    grok.provides(ITemplateUtility)
    grok.name('opengever.templatedossier')

    def templateFolder(self, context):
        catalog = getToolByName(context, 'portal_catalog')
        result = catalog(portal_type="opengever.dossier.templatedossier")
        if result:
            return result[0].getPath()
        return None


def drop_columns(columns):

    cleaned_columns = []

    for col in columns:
        if isinstance(col, dict):
            if col.get('column') in REMOVED_COLUMNS:
                continue
        cleaned_columns.append(col)
    return cleaned_columns


class TemplateDossierDocuments(Documents):
    grok.context(ITemplateDossier)

    @property
    def columns(self):
        return drop_columns(
            super(TemplateDossierDocuments, self).columns)


class TemplateDossierTrash(Trash):
    grok.context(ITemplateDossier)

    @property
    def columns(self):
        return drop_columns(
            super(TemplateDossierTrash, self).columns)
