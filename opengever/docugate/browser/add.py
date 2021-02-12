from opengever.base.behaviors.utils import hide_fields_from_behavior
from opengever.base.interfaces import IRedirector
from opengever.docugate import _
from opengever.docugate.interfaces import IDocumentFromDocugate
from opengever.officeconnector.helpers import create_oc_url
from opengever.propertysheets.form import omit_custom_properties_group
from plone.dexterity.browser import add
from zope.interface import alsoProvides


class DocugateAddForm(add.DefaultAddForm):
    label = _(u'label_add_document_from_docugate',
              default=u'Add document from Docugate template')
    portal_type = 'opengever.document.document'
    skip_validate_file_field = True

    def updateFields(self):
        super(DocugateAddForm, self).updateFields()
        hide_fields_from_behavior(self, ['file'])
        self.groups = omit_custom_properties_group(self.groups)

    def create(self, data):
        doc = super(DocugateAddForm, self).create(data)
        doc.as_shadow_document()
        alsoProvides(doc, IDocumentFromDocugate)
        return doc

    def add(self, object):
        super(DocugateAddForm, self).add(object)
        doc = object.__of__(self.context)

        self.immediate_view = doc.absolute_url()

        redirector = IRedirector(self.request)
        redirector.redirect(create_oc_url(
            self.request,
            doc,
            dict(action='docugate'),
        ))
