from opengever.api.schema.querysources import GEVERQuerySourcesGet
from opengever.contact.sources import PloneSqlOrKubContactSourceBinder
from opengever.ogds.base.sources import AllFilteredGroupsSourceBinder
from opengever.ogds.base.sources import AllUsersAndGroupsSourceBinder
from opengever.ogds.base.sources import CurrentAdminUnitOrgUnitsSourceBinder
from opengever.workspace import is_workspace_feature_enabled
from opengever.workspace import WHITELISTED_TEAMRAUM_PORTAL_TYPES
from plone.supermodel import model
from zope import schema
from zope.schema import getFieldsInOrder


class IGlobalSourceSchema(model.Schema):

    all_users_and_groups = schema.Choice(
        source=AllUsersAndGroupsSourceBinder(only_active_orgunits=False,
                                             include_inactive_groups=True),
    )

    filtered_groups = schema.Choice(
        source=AllFilteredGroupsSourceBinder(),
    )

    current_admin_unit_org_units = schema.Choice(
        source=CurrentAdminUnitOrgUnitsSourceBinder(),
    )

    contacts = schema.Choice(
        source=PloneSqlOrKubContactSourceBinder()
    )


class GlobalSourcesGet(GEVERQuerySourcesGet):

    def reply(self):
        # List of all global sources
        if len(self.params) == 0:
            return [
                {
                    "@id": "{}/@globalsources/{}".format(
                        self.context.absolute_url(), fieldname
                    ),
                    "title": fieldname,
                }
                for fieldname, field in getFieldsInOrder(IGlobalSourceSchema)
                if self.is_visible(fieldname)
            ]

        # Query a specific globalsource
        fieldname = self.params[0]
        field = IGlobalSourceSchema.get(fieldname)
        if not self.is_visible(fieldname) or field is None:
            return self._error(404, "Not Found",
                               "No such globalsource: %r" % fieldname)

        return self.query_and_serialize_results(field, fieldname)

    def is_visible(self, querysource_name):
        if is_workspace_feature_enabled():
            return querysource_name in WHITELISTED_TEAMRAUM_PORTAL_TYPES
        return True
