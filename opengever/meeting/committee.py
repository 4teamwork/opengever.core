from opengever.meeting import _
from opengever.meeting.container import ModelContainer
from opengever.meeting.model import Committee as CommitteeModel
from opengever.meeting.service import meeting_service
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

    def get_unscheduled_proposals(self):
        committee_model = self.load_model()
        return meeting_service().get_submitted_proposals(committee_model)

    def get_model_create_arguments(self, context):
        aq_wrapped_self = self.__of__(context)

        return dict(physical_path=aq_wrapped_self.get_physical_path())

    def get_physical_path(self):
        url_tool = self.unrestrictedTraverse('@@plone_tools').url()
        return '/'.join(url_tool.getRelativeContentPath(self))
