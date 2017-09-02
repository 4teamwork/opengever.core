from opengever.base.interfaces import ISQLObjectWrapper
from plone.directives import form
from zope import schema
from zope.interface import Interface


class IMeetingSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable meeting feature',
        description=u'Whether features from opengever.meeting are enabled',
        default=False)

    is_word_implementation_enabled = schema.Bool(
        title=u'Enable meeting Word implementation',
        description=u'Whether meetings are using the Word implementation',
        default=False)


class IMeetingWrapper(ISQLObjectWrapper):
    """Marker interface for meeting object wrappers."""


class IMemberWrapper(ISQLObjectWrapper):
    """Marker interface for member object wrappers."""


class IMembershipWrapper(ISQLObjectWrapper):
    """Marker interface for membership object wrappers."""


class IPeriodWrapper(ISQLObjectWrapper):
    """Marker interface for period object wrappers."""


class IMeetingDossier(form.Schema):
    """Marker interface for MeetingDossier"""


class IHistory(Interface):
    """History for an object."""
