from opengever.meeting import _
from opengever.meeting.container import ModelContainer
from opengever.meeting.model import Committee as CommitteeModel
from plone.directives import form
from zope import schema
from zope.interface import Interface


class ICommittee(form.Schema):
    """Base schema for the committee.
    """


class ICommitteeModel(Interface):
    """Proposal model schema interface."""

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True,
        max_length=256,
        )


class Committee(ModelContainer):
    """Plone Proxy for a Committe."""

    content_schema = ICommittee
    model_schema = ICommitteeModel
    model_class = CommitteeModel
