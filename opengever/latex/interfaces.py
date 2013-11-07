from zope import schema
from zope.interface import Interface


class ILandscapeLayer(Interface):
    """A request layer for choosing the landscape layout.
    """


class ILaTeXSettings(Interface):
    """opengever.latex settings in the plone.ap.registry."""

    location = schema.TextLine(
        title=u'Location',
        description=u'Possible values for retention period in years.',
        default=u'Bern')
