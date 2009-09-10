
from zope import schema

from plone.directives import form

from opengever.repository import _

class IDocumentSchema(form.Schema):
    """ Document Schema Interface
    """

    foreign_reference = schema.Text(
            title = _(u'label_foreign_reference', default='Fremdzeichen'),
            description = _('help_foreign_reference', default=''),
            required = False,
    )

