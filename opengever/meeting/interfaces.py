from zope import schema
from zope.interface import Interface
from plone.directives import form


class IMeetingSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable meeting feature',
        description=u'Whether features from opengever.meeting are enabled',
        default=False)


class IMeetingWrapper(Interface):
    """Marker interface for meeting object wrappers."""


class IMemberWrapper(Interface):
    """Marker interface for member object wrappers."""


class IMeetingDossier(form.Schema):
    """Marker interface for MeetingDossier"""
