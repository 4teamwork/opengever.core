from ftw.bumblebee.interfaces import IBumblebeeable
from ftw.bumblebee.interfaces import IBumblebeeDocument
from Missing import Value as MissingValue
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.response import IResponseContainer
from opengever.base.response import IResponseSupported
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models.group import Group
from opengever.ogds.models.team import Team
from opengever.ogds.models.user import User
from opengever.repository.interfaces import IRepositoryFolder
from plone import api
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IJsonCompatible
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from plone.restapi.serializer.summary import DefaultJSONSummarySerializer
from Products.ZCatalog.interfaces import ICatalogBrain
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


def extend_with_bumblebee_checksum(result, context):
    if IBumblebeeable.providedBy(context):
        result['bumblebee_checksum'] = IBumblebeeDocument(context).get_checksum()


def extend_with_relative_path(result, context):
    url_tool = api.portal.get_tool(name='portal_url')
    result['relative_path'] = '/'.join(url_tool.getRelativeContentPath(context))


def extend_with_responses(result, context, request):
    if IResponseSupported.providedBy(context):
        result['responses'] = []
        for response in IResponseContainer(context).list():
            serializer = getMultiAdapter((response, request), ISerializeToJson)
            result['responses'].append(serializer(container=context))


@adapter(IDexterityContent, IOpengeverBaseLayer)
class GeverSerializeToJson(SerializeToJson):

    def __call__(self, *args, **kwargs):
        result = super(GeverSerializeToJson, self).__call__(*args, **kwargs)

        extend_with_bumblebee_checksum(result, self.context)
        extend_with_relative_path(result, self.context)
        extend_with_responses(result, self.context, self.request)

        return result


@adapter(IDexterityContainer, IOpengeverBaseLayer)
class GeverSerializeFolderToJson(SerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(GeverSerializeFolderToJson, self).__call__(*args, **kwargs)

        extend_with_relative_path(result, self.context)
        extend_with_responses(result, self.context, self.request)

        return result


@adapter(long)
@implementer(IJsonCompatible)
def long_converter(value):
    """Long is currently not supported by plone.restapi, but should be
    in a later release.
    """
    return value


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
        self.add_additional_metadata(data)
        return data

    def get_columns(self):
        return self.context.__table__.columns

    def add_additional_metadata(self, data):
        pass


@implementer(ISerializeToJson)
@adapter(Team, IOpengeverBaseLayer)
class SerializeTeamModelToJson(SerializeSQLModelToJsonBase):

    content_type = 'virtual.ogds.team'

    def add_additional_metadata(self, data):
        """Add the team members, group summary and org_unit_title"""

        data['users'] = []
        for user in self.context.group.users:
            user_serializer = queryMultiAdapter(
                (user, self.request), ISerializeToJsonSummary)
            data['users'].append(user_serializer())

        data['org_unit_title'] = self.context.org_unit.title

        group_serializer = queryMultiAdapter(
                (self.context.group, self.request), ISerializeToJsonSummary)
        data['group'] = group_serializer()


@implementer(ISerializeToJson)
@adapter(User, IOpengeverBaseLayer)
class SerializeUserModelToJson(SerializeSQLModelToJsonBase):

    content_type = 'virtual.ogds.user'

    def add_additional_metadata(self, data):
        """Add the groups and teams assigned to that user."""

        service = ogds_service()
        groups = service.assigned_groups(self.context.userid)
        data['groups'] = []
        data['teams'] = []
        for group in groups:
            group_serializer = queryMultiAdapter(
                (group, self.request), ISerializeToJsonSummary)
            data['groups'].append(group_serializer())
            for team in group.teams:
                team_serializer = queryMultiAdapter(
                    (team, self.request), ISerializeToJsonSummary)
                data['teams'].append(team_serializer())


@implementer(ISerializeToJsonSummary)
@adapter(Interface, IOpengeverBaseLayer)
class GeverSerializeToJsonSummary(DefaultJSONSummarySerializer):

    def __call__(self, *args, **kwargs):
        summary = super(GeverSerializeToJsonSummary, self).__call__(*args, **kwargs)

        summary['is_subdossier'] = None
        if IDossierMarker.providedBy(self.context) or IDossierTemplateMarker.providedBy(self.context):
            summary['is_subdossier'] = self.context.is_subdossier()

        summary['is_leafnode'] = None
        if IRepositoryFolder.providedBy(self.context):
            summary['is_leafnode'] = self.context.is_leaf_node()

        return summary


@implementer(ISerializeToJsonSummary)
@adapter(ICatalogBrain, IOpengeverBaseLayer)
class SerializeBrainToJsonSummary(DefaultJSONSummarySerializer):

    def __call__(self, *args, **kwargs):
        summary = super(SerializeBrainToJsonSummary, self).__call__(*args, **kwargs)

        if self.context.is_subdossier == MissingValue:
            summary['is_subdossier'] = None
        else:
            summary['is_subdossier'] = self.context.is_subdossier

        summary['is_leafnode'] = None
        if self.context.portal_type == 'opengever.repository.repositoryfolder':
            if self.context.has_sametype_children != MissingValue:
                summary['is_leafnode'] = not self.context.has_sametype_children

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
        base_url = self.request.URL.rsplit("/@")[0]
        return '{}/{}/{}'.format(
            base_url,
            self.endpoint_name,
            getattr(self.context, self.id_attribute_name)
            )

    def add_additional_metadata(self, data):
        pass


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
    endpoint_name = '@team'

    def add_additional_metadata(self, data):
        data['org_unit_title'] = self.context.org_unit.title


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
        'firstname',
        'lastname',
        'phone_office',
        'phone_mobile',
        'phone_fax',
        'userid',
    )

    content_type = 'virtual.ogds.user'
    id_attribute_name = 'userid'
    endpoint_name = '@ogds-user'

    def add_additional_metadata(self, data):
        data['title'] = self.context.fullname()


@implementer(ISerializeToJsonSummary)
@adapter(Group, IOpengeverBaseLayer)
class SerializeGroupModelToJsonSummary(SerializeSQLModelToJsonSummaryBase):

    item_columns = (
        'groupid',
        'title',
        'active',
    )

    content_type = 'virtual.ogds.group'
    id_attribute_name = 'groupid'
    endpoint_name = '@group'
