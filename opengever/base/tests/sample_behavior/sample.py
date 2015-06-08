from plone.directives import form
from zope import schema
from zope.interface import alsoProvides


class ISampleSchema(form.Schema):
    """Sample behavior to be used in tests.
    """

    foobar = schema.Int(
        title=u'Foobar',
        required=False,
        default=42
    )

alsoProvides(ISampleSchema, form.IFormFieldProvider)
