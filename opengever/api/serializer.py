from Acquisition import aq_inner
from Missing import Value as MissingValue
from opengever.api.batch import SQLHypermediaBatch
from opengever.base.behaviors.sequence import ISequenceNumberBehavior
from opengever.base.behaviors.translated_title import get_inactive_languages
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.interfaces import ISequenceNumber
from opengever.base.oguid import Oguid
from opengever.base.response import IResponseContainer
from opengever.base.response import IResponseSupported
from opengever.base.utils import is_administrator
from opengever.base.visible_users_and_groups_filter import visible_users_and_groups_filter
from opengever.document import is_documentish_portal_type
from opengever.document.approvals import Approval
from opengever.document.behaviors import IBaseDocument
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.utils import is_dossierish_portal_type
from opengever.dossier.utils import supports_is_subdossier
from opengever.ogds.base.actor import Actor
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.ogds.models.group import Group
from opengever.ogds.models.group_membership import GroupMembership
from opengever.ogds.models.group_membership import groups_users
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.team import Team
from opengever.ogds.models.user import User
from opengever.private.folder import IPrivateFolder
from opengever.repository.interfaces import IRepositoryFolder
from opengever.workspaceclient import is_workspace_client_feature_enabled
from plone import api
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import IJsonCompatible
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from plone.restapi.serializer.group import SerializeGroupToJson
from plone.restapi.serializer.relationfield import RelationListFieldSerializer
from plone.restapi.serializer.summary import DEFAULT_METADATA_FIELDS
from plone.restapi.serializer.summary import DefaultJSONSummarySerializer
from Products.PlonePAS.interfaces.group import IGroupData
from Products.ZCatalog.interfaces import ICatalogBrain
from sqlalchemy import func
from z3c.relationfield.interfaces import IRelationList
from zc.relation.interfaces import ICatalog
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import Interface
from zope.intid.interfaces import IIntIds
import logging


logger = logging.getLogger('opengever.api.serializer')

DEFAULT_METADATA_FIELDS.add('UID')


def extend_with_oguid(result, context):
    try:
        oguid = Oguid.for_object(context).id
    except Exception as exc:
        logger.warn('Failed to determine Oguid for %r - %r' % (context, exc))
        oguid = None

    result['oguid'] = oguid


def extend_with_relative_path(result, context):
    url_tool = api.portal.get_tool(name='portal_url')
    result['relative_path'] = '/'.join(url_tool.getRelativeContentPath(context))


def extend_with_responses(result, context, request):
    if IResponseSupported.providedBy(context):
        result['responses'] = []
        for response in IResponseContainer(context).list():
            serializer = getMultiAdapter((response, request), ISerializeToJson)
            result['responses'].append(serializer(container=context))


def extend_with_sequence_number(result, context, request):
    if ISequenceNumberBehavior.providedBy(context):
        result['sequence_number'] = getUtility(
            ISequenceNumber).get_number(context)


def extend_with_is_subdossier(result, context, request):
    if supports_is_subdossier(context):
        result['is_subdossier'] = context.is_subdossier()


def extend_with_dossier_type(result, context, request):
    if IDossierMarker.providedBy(context):
        result['dossier_type'] = IDossier(context).dossier_type


def extend_with_is_locked_by_copy_to_workspace(result, context, request):
    if is_workspace_client_feature_enabled():
        result['is_locked_by_copy_to_workspace'] = \
            context.is_locked_by_copy_to_workspace()


def extend_with_groupurl(result, context, request):
    """OGDS-Groups cannot be modified by default nor are all metadata stored
    in the ogds. The `@groups` endpoint provides more information about
    a group and it also provides the PATCH and POST verbs to modify a
    group. We extend the response data with the `groupurl`
    which is a URL to the group-resource stored in plone, not in the ogds.
    """
    result['groupurl'] = '{}/@groups/{}'.format(
        api.portal.get().absolute_url(), context.groupid)


def extend_with_backreferences(result, context, request, reference_attribute_name,
                               documents_only=False):
    """Extend the given result dict with an additional key
    `back_references_{reference_attribute_name}` for example
    `back_references_relatedDossiers` and a list of backreferences.
    """
    summaries = []
    intids = getUtility(IIntIds)
    catalog = getUtility(ICatalog)
    relations = catalog.findRelations(
        {'to_id': intids.getId(aq_inner(context)),
         'from_attribute': reference_attribute_name})

    # Filter non-documentish types for document-to-document relations
    if documents_only:
        relations = filter(
            lambda rel: IBaseDocument.providedBy(rel.from_object),
            relations)

    summaries = [
        getMultiAdapter((relation.from_object, request), ISerializeToJsonSummary)()
        for relation in relations]

    attribute_name = 'back_references_{}'.format(reference_attribute_name)
    result[attribute_name] = summaries


def drop_inactive_language_fields(result):
    for lang in get_inactive_languages():
        field_name = 'title_{}'.format(lang)
        if field_name in result:
            del result[field_name]


@adapter(IDexterityContent, IOpengeverBaseLayer)
class GeverSerializeToJson(SerializeToJson):

    def __call__(self, *args, **kwargs):
        result = super(GeverSerializeToJson, self).__call__(*args, **kwargs)

        extend_with_oguid(result, self.context)
        extend_with_relative_path(result, self.context)
        extend_with_responses(result, self.context, self.request)
        extend_with_sequence_number(result, self.context, self.request)

        drop_inactive_language_fields(result)
        return result


@adapter(IDexterityContainer, IOpengeverBaseLayer)
class GeverSerializeFolderToJson(SerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(GeverSerializeFolderToJson, self).__call__(*args, **kwargs)

        extend_with_oguid(result, self.context)
        extend_with_relative_path(result, self.context)
        extend_with_responses(result, self.context, self.request)
        extend_with_is_subdossier(result, self.context, self.request)
        extend_with_sequence_number(result, self.context, self.request)

        drop_inactive_language_fields(result)
        return result


@adapter(IPrivateFolder, IOpengeverBaseLayer)
class GeverSerializePrivateFolderToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(GeverSerializePrivateFolderToJson, self).__call__(*args, **kwargs)
        result['title'] = self.context.title
        return result


@adapter(IRelationList, IDexterityContent, IOpengeverBaseLayer)
@implementer(IFieldSerializer)
class GeverRelationListFieldSerializer(RelationListFieldSerializer):

    def __call__(self):
        value = super(RelationListFieldSerializer, self).__call__()
        return [item for item in value if item is not None]


@adapter(long)
@implementer(IJsonCompatible)
def long_converter(value):
    """Long is currently not supported by plone.restapi, but should be
    in a later release.
    """
    return value


@adapter(Oguid)
@implementer(IJsonCompatible)
def oguid_converter(value):
    """Returns the id for the Oguid object.
    """
    return value.id


@adapter(Approval)
@implementer(IJsonCompatible)
def approval_converter(approval):
    task = approval.get_task_brain()

    # If the task is not accessible for the current user task is None
    if task:
        task = getMultiAdapter((approval.get_task_brain(), getRequest()),
                               ISerializeToJsonSummary)()

    return json_compatible({
        'approved': approval.approved,
        'approver': approval.approver,
        'task': task,
        'version_id': approval.version_id,
    })


class SerializeSQLModelToJsonBase(object):

    content_type = ''

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, *args, **kwargs):
        data = {}
        for col in self.get_columns():
            key = self.context.__mapper__.get_property_by_column(col).key
            data[key] = json_compatible(getattr(self.context, key))

        data['@type'] = self.content_type
        data['@id'] = self.request.URL
        self.add_batched_items(data)
        self.add_additional_metadata(data)
        return data

    def get_columns(self):
        return self.context.__table__.columns

    def add_additional_metadata(self, data):
        pass

    def get_item_query(self):
        pass

    def add_batched_items(self, data):
        query = self.get_item_query()
        if not query:
            return
        batch = SQLHypermediaBatch(self.request, query, 'userid')
        items = [queryMultiAdapter((item, self.request), ISerializeToJsonSummary)()
                 for item in batch]

        data['items_total'] = batch.items_total
        data['items'] = items

        if batch.links:
            data['batching'] = batch.links


@implementer(ISerializeToJson)
@adapter(Team, IOpengeverBaseLayer)
class SerializeTeamModelToJson(SerializeSQLModelToJsonBase):

    content_type = 'virtual.ogds.team'

    def __call__(self, *args, **kwargs):
        data = super(SerializeTeamModelToJson, self).__call__(*args, **kwargs)

        data['@id'] = '{}/@teams/{}'.format(
            api.portal.get().absolute_url(),
            self.context.team_id)

        return data

    def get_item_query(self):
        # The teammembers are the items of the team
        users = User.query.join(groups_users).filter_by(
            groupid=self.context.groupid).order_by(User.lastname)
        return users

    def add_additional_metadata(self, data):
        """Add group summary and org_unit_title"""
        data['org_unit_title'] = self.context.org_unit.title

        group_serializer = queryMultiAdapter(
            (self.context.group, self.request), ISerializeToJsonSummary)
        data['group'] = group_serializer()


@implementer(ISerializeToJson)
@adapter(Group, IOpengeverBaseLayer)
class SerializeGroupModelToJson(SerializeSQLModelToJsonBase):

    content_type = 'virtual.ogds.group'

    def get_item_query(self):
        # The group members are the items of the group
        users = User.query.join(groups_users).filter_by(
            groupid=self.context.groupid).order_by(User.lastname)
        return users

    def add_additional_metadata(self, data):
        extend_with_groupurl(data, self.context, self.request)


@implementer(ISerializeToJson)
@adapter(IGroupData, IOpengeverBaseLayer)
class GeverSerializeGroupToJson(SerializeGroupToJson):

    content_type = 'virtual.plone.group'

    def __call__(self):
        data = self.base_group_info()
        data['@type'] = self.content_type

        data["users"] = self.member_data()

        # The user-items are just userids by default which is not the expected
        # response for summarized users. We have to extend the items manually
        # with additional metadata to make this endpoint behaves like other ones.
        user_items = []
        for userid in data.get('users').get('items'):
            user_items.append({
                '@id': '{}/@users/{}'.format(api.portal.get().absolute_url(), userid),
                '@type': 'virtual.plone.user',
                'token': userid,
                'title': Actor.lookup(userid).get_label()
            })

        data.get('users')['items'] = user_items
        return data

    def base_group_info(self):
        group = self.context
        portal = api.portal.get()

        return {
            "@id": "{}/@groups/{}".format(portal.absolute_url(), group.id),
            "id": group.id,
            "groupname": group.getGroupName(),
            "email": group.getProperty("email"),
            "title": group.getProperty("title"),
            "description": group.getProperty("description"),
            "roles": group.getRoles(),
        }

    def member_data(self):
        # Get group member ids in a more performant way than in plone.restapi
        # which calls `group.getGroupMemberIds()` which is incredibly slow
        # for a larger amount of group members.
        gtool = api.portal.get_tool(name='portal_groups')
        members = gtool.getGroupMembers(self.context.getId())
        batch = HypermediaBatch(self.request, members)
        users_data = {
            "@id": batch.canonical_url,
            "items_total": batch.items_total,
            "items": sorted(batch),
        }
        if batch.links:
            users_data["batching"] = batch.links
        return users_data


@implementer(ISerializeToJson)
@adapter(User, IOpengeverBaseLayer)
class SerializeUserModelToJson(SerializeSQLModelToJsonBase):

    content_type = 'virtual.ogds.user'

    def add_additional_metadata(self, data):
        """Add the groups and teams assigned to that user."""
        groups = self.assigned_groups()
        teams = self.assigned_teams()
        data['groups'] = []
        data['teams'] = []

        if not visible_users_and_groups_filter.can_access_all_principals():
            return

        for group in groups:
            group_serializer = queryMultiAdapter(
                (group, self.request), ISerializeToJsonSummary)
            data['groups'].append(group_serializer())

        for team in teams:
            team_serializer = queryMultiAdapter(
                (team, self.request), ISerializeToJsonSummary)
            data['teams'].append(team_serializer())

        groupids = [group.get('groupid') for group in data['groups']]

        rows = (
            GroupMembership.query
            .with_entities(GroupMembership.groupid, GroupMembership.note)
            .filter(
                GroupMembership.userid == self.context.userid,
                GroupMembership.groupid.in_(groupids),
                GroupMembership.note.isnot(None),
            )
            .all()
        )

        notes_by_groupid = dict(rows)

        for group in data['groups']:
            note = notes_by_groupid.get(group.get("groupid"))
            if note:
                group["note"] = note

    def __call__(self, *args, **kwargs):
        data = super(SerializeUserModelToJson, self).__call__(*args, **kwargs)
        if not is_administrator():
            del data['last_login']

        # Rename the attribute name for the title SQL column on the User model
        # to 'job_title' in order to stay consistent with *summary* serializers
        # for OGDS objects, where 'title' is a special computed field used as
        # a display label.
        data['job_title'] = data.pop('title')

        return data

    def assigned_groups(self):
        """Returns the assigned_groups for a given user ordered by the title
        or groupid.

        The group title is not required. Thus, we need to use the title or the
        groupid for sorting. Using the `coalesce` function could lead into
        performance issues with a huge amount of groups or queries.

        Currently, we don't want this function in the ogds_service until we have
        a good solution to not lead into performance issues.
        """
        query = Group.query.join(Group.users)
        query = query.filter(User.userid == self.context.userid)

        # Order by title or groupid if no title is given.
        query = query.order_by(func.coalesce(Group.title, Group.groupid))

        return query.all()

    def assigned_teams(self):
        """Returns the assigned_teams for the given user ordered by the title.
        """
        query = Team.query.join(Group).join(Group.users)
        query = query.filter(User.userid == self.context.userid)
        query = query.order_by(Team.title)
        return query.all()


@implementer(ISerializeToJsonSummary)
@adapter(Interface, IOpengeverBaseLayer)
class GeverSerializeToJsonSummary(DefaultJSONSummarySerializer):

    def __call__(self, *args, **kwargs):
        summary = super(GeverSerializeToJsonSummary, self).__call__(*args, **kwargs)

        extend_with_is_subdossier(summary, self.context, self.request)
        extend_with_dossier_type(summary, self.context, self.request)

        if 'oguid' in self.metadata_fields():
            extend_with_oguid(summary, self.context)

        summary['is_leafnode'] = None
        if IRepositoryFolder.providedBy(self.context):
            summary['is_leafnode'] = self.context.is_leaf_node()

        if IBaseDocument.providedBy(self.context):
            summary['checked_out'] = self.context.checked_out_by()
            summary['file_extension'] = self.context.get_file_extension()
            extend_with_is_locked_by_copy_to_workspace(summary, self.context, self.request)

        return summary


@implementer(ISerializeToJsonSummary)
@adapter(ICatalogBrain, IOpengeverBaseLayer)
class SerializeBrainToJsonSummary(DefaultJSONSummarySerializer):

    def __call__(self, *args, **kwargs):
        summary = super(SerializeBrainToJsonSummary, self).__call__(*args, **kwargs)

        if is_dossierish_portal_type(self.context.portal_type):
            summary['is_subdossier'] = None
            if self.context.is_subdossier != MissingValue:
                summary['is_subdossier'] = self.context.is_subdossier

        summary['is_leafnode'] = None
        if self.context.portal_type == 'opengever.repository.repositoryfolder':
            if self.context.has_sametype_children != MissingValue:
                summary['is_leafnode'] = not self.context.has_sametype_children

        if is_documentish_portal_type(self.context.portal_type):
            summary['checked_out'] = self.context.checked_out
            summary['file_extension'] = self.context.file_extension

        return summary


class SerializeSQLModelToJsonSummaryBase(object):

    item_columns = tuple()
    content_type = ''
    id_attribute_name = ''
    endpoint_name = ''

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, *args, **kwargs):
        data = {}
        for colname in self.item_columns:
            data[colname] = json_compatible(getattr(self.context, colname))

        data['@type'] = self.content_type
        data['@id'] = self.get_url
        self.add_additional_metadata(data)
        return data

    @property
    def get_url(self):
        return u'{}/{}/{}'.format(
            self.base_url,
            self.endpoint_name,
            getattr(self.context, self.id_attribute_name)
        )

    def add_additional_metadata(self, data):
        pass

    @property
    def base_url(self):
        return self.request.URL.rsplit("/@")[0]


@implementer(ISerializeToJsonSummary)
@adapter(Team, IOpengeverBaseLayer)
class SerializeTeamModelToJsonSummary(SerializeSQLModelToJsonSummaryBase):

    item_columns = (
        'active',
        'groupid',
        'org_unit_id',
        'team_id',
        'title',
    )

    content_type = 'virtual.ogds.team'
    id_attribute_name = 'team_id'
    endpoint_name = '@teams'

    def add_additional_metadata(self, data):
        data['org_unit_title'] = self.context.org_unit.title

    @property
    def get_url(self):
        return '{}/{}/{}'.format(
            api.portal.get().absolute_url(),
            self.endpoint_name,
            getattr(self.context, self.id_attribute_name)
        )


@implementer(ISerializeToJsonSummary)
@adapter(User, IOpengeverBaseLayer)
class SerializeUserModelToJsonSummary(SerializeSQLModelToJsonSummaryBase):

    item_columns = (
        'active',
        'department',
        'directorate',
        'email',
        'email2',
        'firstname',
        'lastname',
        'phone_office',
        'phone_mobile',
        'phone_fax',
        'userid',
        'username',
    )

    content_type = 'virtual.ogds.user'
    id_attribute_name = 'userid'
    endpoint_name = '@ogds-users'

    def add_additional_metadata(self, data):
        data['title'] = self.context.fullname()

        # The `title` field (as it's called on the SQL model) would conflict
        # with the already existing `title` that is used as a display label.
        data['job_title'] = self.context.title

        if is_administrator():
            attrs = [
                'address1',
                'address2',
                'city',
                'country',
                'department_abbr',
                'description',
                'directorate_abbr',
                'last_login',
                'organization',
                'salutation',
                'zip_code',
            ]
            for attr in attrs:
                value = json_compatible(getattr(self.context, attr, None))
                data[attr] = value

    @property
    def base_url(self):
        return api.portal.get().absolute_url()


@implementer(ISerializeToJsonSummary)
@adapter(Group, IOpengeverBaseLayer)
class SerializeGroupModelToJsonSummary(SerializeSQLModelToJsonSummaryBase):

    item_columns = (
        'groupid',
        'groupname',
        'title',
        'active',
        'is_local',
    )

    content_type = 'virtual.ogds.group'
    id_attribute_name = 'groupid'
    endpoint_name = '@ogds-groups'

    def add_additional_metadata(self, data):
        extend_with_groupurl(data, self.context, self.request)

    @property
    def base_url(self):
        return api.portal.get().absolute_url()


@implementer(ISerializeToJsonSummary)
@adapter(AdminUnit, IOpengeverBaseLayer)
class SerializeAdminUnitModelToJsonSummary(SerializeSQLModelToJsonSummaryBase):

    item_columns = (
        'unit_id',
        'title',
        'public_url',
        'abbreviation',
        'enabled',
        'hidden',
    )

    content_type = 'virtual.ogds.admin_unit'
    id_attribute_name = 'unit_id'
    endpoint_name = '@admin-units'

    def add_additional_metadata(self, data):
        """Add list of org_units summaries"""

        data['org_units'] = [
            queryMultiAdapter((org_unit, self.request), ISerializeToJson)()
            for org_unit in self.context.org_units]


@implementer(ISerializeToJson)
@adapter(OrgUnit, IOpengeverBaseLayer)
class SerializeOrgUnitModelToJsonSummary(SerializeSQLModelToJsonSummaryBase):
    """OrgUnit model json serializer."""

    item_columns = (
        'unit_id',
        'title',
        'enabled',
        'hidden',
    )

    content_type = 'virtual.ogds.org_unit'
    id_attribute_name = 'unit_id'
    endpoint_name = '@org-units'
