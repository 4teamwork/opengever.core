from five import grok
from ftw.table import helper
from ftw.table.interfaces import ITableGenerator
from opengever.base.interfaces import IRedirector
from opengever.dossier import _
from opengever.dossier.interfaces import ITemplateDossierProperties
from opengever.dossier.templatedossier.create import DocumentFromTemplate
from opengever.dossier.templatedossier.interfaces import ITemplateUtility
from opengever.tabbedview.helper import linked
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility
from zope.interface import Interface


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
        # TODO: Add registry option to globally disable docproperty code

        registry = getUtility(IRegistry)
        props = registry.forInterface(ITemplateDossierProperties)

        return DocumentFromTemplate(template_doc).create_in(
            self.context,
            self.title,
            with_properties=props.create_doc_properties
        )

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
