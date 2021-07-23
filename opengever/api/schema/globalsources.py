from opengever.api.schema.querysources import GEVERQuerySourcesGet
from opengever.ogds.base.sources import AllFilteredGroupsSourceBinder
from opengever.ogds.base.sources import AllUsersAndGroupsSourceBinder
from opengever.ogds.base.sources import CurrentAdminUnitOrgUnitsSourceBinder
from plone.supermodel import model
from zope import schema
from zope.schema import getFieldsInOrder


class IGlobalSourceSchema(model.Schema):

    all_users_and_groups = schema.Choice(
        source=AllUsersAndGroupsSourceBinder(),
    )

    filtered_groups = schema.Choice(
        source=AllFilteredGroupsSourceBinder(),
    )

    current_admin_unit_org_units = schema.Choice(
        source=CurrentAdminUnitOrgUnitsSourceBinder(),
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
            ]

        # Query a specific globalsource
        fieldname = self.params[0]
        field = IGlobalSourceSchema.get(fieldname)
        if field is None:
            return self._error(404, "Not Found",
                               "No such globalsource: %r" % fieldname)

        return self.query_and_serialize_results(field, fieldname)
