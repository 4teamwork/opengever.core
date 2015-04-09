from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.meeting import _
from opengever.meeting.container import ModelContainer
from opengever.meeting.model import Committee as CommitteeModel
from opengever.meeting.model import Meeting
from opengever.meeting.model import Membership
from opengever.meeting.service import meeting_service
from plone import api
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

    def Title(self):
        model = self.load_model()
        if not model:
            return ''
        return model.title

    def get_unscheduled_proposals(self):
        committee_model = self.load_model()
        return meeting_service().get_submitted_proposals(committee_model)

    def get_model_create_arguments(self, context):
        aq_wrapped_self = self.__of__(context)

        return dict(physical_path=aq_wrapped_self.get_physical_path())

    def get_physical_path(self):
        url_tool = api.portal.get_tool(name='portal_url')
        return '/'.join(url_tool.getRelativeContentPath(self))

    def get_active_memberships(self):
        return Membership.query.filter_by(
            committee=self.load_model()).only_active()

    def get_memberships(self):
        return self.load_model().memberships

    def is_editable(self):
        """A committee is always editable."""

        return True

    def get_upcoming_meetings(self):
        committee_model = self.load_model()
        return Meeting.query.all_upcoming_meetings(committee_model)

    def get_pre_protocol_template(self):
        container = aq_parent(aq_inner(self))
        return container.get_pre_protocol_template()

    def get_protocol_template(self):
        container = aq_parent(aq_inner(self))
        return container.get_protocol_template()

    def get_excerpt_template(self):
        container = aq_parent(aq_inner(self))
        return container.get_excerpt_template()
