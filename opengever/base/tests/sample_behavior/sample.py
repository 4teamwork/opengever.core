from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides


class ISampleSchema(model.Schema):
    """Sample behavior to be used in tests.
    """

    foobar = schema.Int(
        title=u'Foobar',
        required=False,
        default=42
    )

alsoProvides(ISampleSchema, IFormFieldProvider)
