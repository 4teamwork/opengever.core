from opengever.base.interfaces import ISQLObjectWrapper
from plone.supermodel import model
from zope import schema
from zope.interface import Interface


class IMeetingSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable meeting feature',
        description=u'Whether features from opengever.meeting are enabled',
        default=False)

    sablon_date_format_string = schema.TextLine(
        title=u'Date formatting string for sablon templates',
        description=u'Formatting string used to format date fields for sablon templates',
        default=u'%d.%m.%Y')


class IMeetingTemplate(model.Schema):

    pass


class IParagraphTemplate(model.Schema):

    pass


class IMeetingWrapper(ISQLObjectWrapper):
    """Marker interface for meeting object wrappers."""


class IMemberWrapper(ISQLObjectWrapper):
    """Marker interface for member object wrappers."""


class IMembershipWrapper(ISQLObjectWrapper):
    """Marker interface for membership object wrappers."""


class IMeetingDossier(model.Schema):
    """Marker interface for MeetingDossier"""


class IDuringMeetingMigration(Interface):
    """Request layer to indicate that meetings are being migrated
    to prepare deletion of the meeting feature. It is used to skip certain
    checks that would prevent the migration.
    """


class IProposalLikeContent(Interface):
    """Marker interface for the old style proposals and the new ris
    proposals.

    We use this marker interface to provide a listing with both types.
    """
