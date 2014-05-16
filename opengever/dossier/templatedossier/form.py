from five import grok
from ftw.table import helper
from ftw.table.interfaces import ITableGenerator
from opengever.base.interfaces import IRedirector
from opengever.dossier import _
from opengever.dossier.templatedossier.interfaces import ITemplateUtility
from opengever.tabbedview.helper import linked
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import iterSchemata
from plone.rfc822.interfaces import IPrimaryField
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form.interfaces import IValue
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFieldsInOrder


NO_DEFAULT_VALUE_FIELDS = ['title', 'file']


class TemplateDocumentFormView(grok.View):
    """Show the "Document from template" form.

    This form lists available document templates from template dossiers,
    allows the user to select one and creates a new document by copying the
    template.
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
        self.edit_after_creation = False

        if self.request.get('form.buttons.save'):

            # Extract required parameters from the request
            template_path = None
            if self.request.get('paths'):
                template_path = self.request.get('paths')[0]
            self.title = self.request.get('form.title', '').decode('utf8')
            self.edit_after_creation = self.request.get(
                'form.widgets.edit_form') == ['on']

            if template_path and self.title:
                new_doc = self.create_document(template_path)

                if self.edit_after_creation:
                    self.activate_external_editing(new_doc)

                    return self.request.RESPONSE.redirect(
                        new_doc.absolute_url())

                return self.request.RESPONSE.redirect(
                    self.context.absolute_url() + '#documents')

            else:
                if template_path is None:
                    self.errors['paths'] = True
                if not self.title:
                    self.errors['title'] = True

        elif self.request.get('form.buttons.cancel'):
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        return self.render_form()

    def activate_external_editing(self, new_doc):
        """Check out the given document, and add the external_editor URL
        to redirector queue.
        """

        # Check out the new document
        manager = self.context.restrictedTraverse('checkout_documents')
        manager.checkout(new_doc)

        # Add redirect to the zem-file download,
        # in order to start editing with external editor.
        redirector = IRedirector(self.request)
        redirector.redirect(
            '%s/external_edit' % new_doc.absolute_url(),
            target='_self',
            timeout=1000)

    def create_document(self, template_path):
        """Create a new document based on a template:

        - Create a new opengever.document.document object
        - Store a copy of the template in its primary file field
        - Update its fields with default values
        """

        template_doc = self.context.restrictedTraverse(template_path)
        _type = self._get_primary_field_type(template_doc)

        new_file = _type(data=template_doc.file.data,
                         filename=template_doc.file.filename)

        new_doc = createContentInContainer(
            self.context, 'opengever.document.document',
            title=self.title, file=new_file)

        self._set_defaults(new_doc)

        # Notify necessary standard event handlers
        notify(ObjectModifiedEvent(new_doc))

        return new_doc

    def _get_primary_field_type(self, obj):
        """Determine the type of an objects primary field (e.g. NamedBlobFile)
        so we can use it as a factory when setting the new document's primary
        field.
        """

        for schemata in iterSchemata(obj):
            for name, field in getFieldsInOrder(schemata):
                if IPrimaryField.providedBy(field):
                    return field._type

    def _set_defaults(self, obj):
        """Set default values for all fields including behavior fields."""

        for schemata in iterSchemata(obj):
            for name, field in getFieldsInOrder(schemata):
                if name not in NO_DEFAULT_VALUE_FIELDS:
                    default = queryMultiAdapter(
                        (obj, obj.REQUEST, None, field, None),
                        IValue, name='default')

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
        """Get the list of template documents and render the "document from
        template" form
        """

        template_util = getUtility(
            ITemplateUtility, 'opengever.templatedossier')
        self.templatedossier = template_util.templateFolder(self.context)
        if self.templatedossier is None:
            status = IStatusMessage(self.request)
            status.addStatusMessage(
                _("Not found the templatedossier"), type="error")
            return self.context.request.RESPONSE.redirect(
                self.context.absolute_url())
        return super(TemplateDocumentFormView, self).__call__()

    def templates(self):
        """List the available template documents the user can choose from.
        """
        generator = getUtility(ITableGenerator, 'ftw.tablegenerator')
        catalog = getToolByName(self.context, 'portal_catalog')
        templates = catalog(
            path=dict(
                depth=-1, query=self.templatedossier),
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
