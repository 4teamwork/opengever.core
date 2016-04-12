from zope import schema
from zope.interface import Interface
from plone.directives import form


class IMeetingSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable meeting feature',
        description=u'Whether features from opengever.meeting are enabled',
        default=False)


class IBaseWrapper(Interface):
    """Marker interface for sql object wrappers."""


class IMeetingWrapper(IBaseWrapper):
    """Marker interface for meeting object wrappers."""


class IMemberWrapper(IBaseWrapper):
    """Marker interface for member object wrappers."""


class IMembershipWrapper(IBaseWrapper):
    """Marker interface for membership object wrappers."""


class IMeetingDossier(form.Schema):
    """Marker interface for MeetingDossier"""
