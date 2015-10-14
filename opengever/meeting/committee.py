from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.meeting import _
from opengever.meeting.committeeroles import CommitteeRoles
from opengever.meeting.container import ModelContainer
from opengever.meeting.model import Committee as CommitteeModel
from opengever.meeting.model import Meeting
from opengever.meeting.model import Membership
from opengever.meeting.service import meeting_service
from opengever.meeting.sources import repository_folder_source
from opengever.meeting.sources import sablon_template_source
from opengever.meeting.wrapper import MeetingWrapper
from opengever.ogds.base.utils import ogds_service
from plone import api
from plone.directives import form
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


@grok.provider(IContextSourceBinder)
def get_group_vocabulary(context):
    service = ogds_service()
    groups = []
    for group in service.all_groups():
        groups.append(SimpleVocabulary.createTerm(
            group.groupid, group.groupid, group.title))
    return SimpleVocabulary(groups)


class ICommittee(form.Schema):
    """Base schema for the committee.
    """

    protocol_template = RelationChoice(
        title=_('Protocol template'),
        source=sablon_template_source,
        required=False,
    )

    excerpt_template = RelationChoice(
        title=_('Excerpt template'),
        source=sablon_template_source,
        required=False,
    )

    repository_folder = RelationChoice(
        title=_(u'Linked repository folder'),
        description=_(
            u'label_linked_repository_folder',
            default=u'Contains automatically generated dossiers and documents '
                    u'for this committee.'),
        source=repository_folder_source,
        required=True)


class ICommitteeModel(Interface):
    """Proposal model schema interface."""

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True,
        max_length=256,
        )

    group_id = schema.Choice(
        title=_('label_group', default="Group"),
        source=get_group_vocabulary,
        required=True,
    )


_marker = object()

class Committee(ModelContainer):
    """Plone Proxy for a Committe."""

    content_schema = ICommittee
    model_schema = ICommitteeModel
    model_class = CommitteeModel

    def _getOb(self, id_, default=_marker):
        """We extend `_getObj` in order to change the context for meeting
        objects to the `MeetingWrapper`. That allows us to register the
        meetings view as regular Browser view without any traversal hacks."""

        obj = super(Committee, self)._getOb(id_, default)
        if obj is not default:
            return obj

        if id_.startswith('meeting'):
            meeting_id = int(id_.split('-')[-1])
            meeting = Meeting.query.get(meeting_id)
            if meeting:
                return MeetingWrapper.wrap(self, meeting)

        if default is _marker:
            raise KeyError(id_)
        return default

    def Title(self):
        model = self.load_model()
        if not model:
            return ''
        return model.title

    def get_unscheduled_proposals(self):
        committee_model = self.load_model()
        return meeting_service().get_submitted_proposals(committee_model)

    def update_model_create_arguments(self, data, context):
        aq_wrapped_self = self.__of__(context)
        data['physical_path'] = aq_wrapped_self.get_physical_path()

    def _after_model_created(self, model_instance):
        super(Committee, self)._after_model_created(model_instance)
        CommitteeRoles(model_instance.group_id).initialize(self)

    def update_model(self, data):
        model = self.load_model()
        if 'group_id' in data and data['group_id'] != model.group_id:
            CommitteeRoles(data['group_id'],
                           previous_group_id=model.group_id).update(self)

        return super(Committee, self).update_model(data)

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

    def get_committee_container(self):
        return aq_parent(aq_inner(self))

    def get_protocol_template(self):
        if self.protocol_template:
            return self.protocol_template.to_object

        return self.get_committee_container().get_protocol_template()

    def get_excerpt_template(self):
        if self.excerpt_template:
            return self.excerpt_template.to_object

        return self.get_committee_container().get_excerpt_template()
