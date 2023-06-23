from opengever.api.dossier_participations import available_roles
from opengever.api.dossier_participations import primary_participation_roles
from opengever.propertysheets.api.base import PropertySheetAPIBase
from opengever.propertysheets.metaschema import IPropertySheetDefinition
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone.restapi.services import Service
from plone.restapi.types.interfaces import IJsonSchemaProvider
from zope.component import getMultiAdapter


class SystemInformationGet(Service):
    """GEVER system information"""

    def reply(self):
        infos = {}
        self.add_dossier_participation_roles(infos)
        self.add_property_sheet_information(infos)
        return infos

    def add_dossier_participation_roles(self, infos):
        available_participation_roles = available_roles(self.context)
        primary_participation_role_ids = {
            role.get('token') for role
            in primary_participation_roles(self.context)}
        for role in available_participation_roles:
            role['primary'] = role.get('token') in primary_participation_role_ids
        infos['dossier_participation_roles'] = available_participation_roles

    def add_property_sheet_information(self, infos):
        # Get translated assignment values
        assignments_schema = getMultiAdapter(
            (IPropertySheetDefinition.get('assignments'), self.context, self.request),
            IJsonSchemaProvider,).get_schema()

        property_sheet_slot_translations = {}
        for [slot_id, title] in assignments_schema.get('items').get('choices'):
            property_sheet_slot_translations[slot_id] = title

        # Then serialize the property-sheets and use the translated assignment title
        property_sheet_api = PropertySheetAPIBase()
        property_sheet_api.request = self.request
        propertysheets = {}
        for sheet in PropertySheetSchemaStorage().list():
            serialized_sheet = property_sheet_api.serialize(sheet)
            serialized_sheet['assignments'] = [
                {
                    'id': assignment_id,
                    'title': property_sheet_slot_translations.get(
                        assignment_id, assignment_id)
                } for assignment_id in serialized_sheet.get('assignments')
            ]
            propertysheets[sheet.name] = serialized_sheet
        infos['property_sheets'] = propertysheets
