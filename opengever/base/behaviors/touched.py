from opengever.base import _
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides


class ITouched(model.Schema):
    """ ITouched contains the touched field tracking
    when an object or its content was last modified.
    """

    # Omitted because it must not be updated manually, only by event handlers.
    form.omitted('touched')
    touched = schema.Date(
        title=_(u'label_touched',
                default=u'Date of modification of the object or its content'),
        required=False,
        readonly=True,
        default=None,
    )


alsoProvides(ITouched, IFormFieldProvider)
