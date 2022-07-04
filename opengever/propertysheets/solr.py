from ftw.solr.handlers import DefaultIndexHandler
from ftw.solr.handlers import DexterityItemIndexHandler
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.dossier.behaviors.customproperties import IDossierCustomProperties
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from zope.schema import getFields


class CustomPropertiesIndexHandler(DefaultIndexHandler):
    """Indexes custom properties in Solr dynamic fields"""

    behavior = None

    def get_data(self, attributes):
        data = super(CustomPropertiesIndexHandler, self).get_data(attributes)
        if not attributes:
            data.update(self.get_custom_properties())
        return data

    def get_custom_properties(self):
        data = {}

        adapted = self.behavior(self.context, None)
        if not adapted:
            return data

        custom_properties = adapted.get_plain_values('custom_properties')
        if not custom_properties:
            return data

        field = getFields(self.behavior).get('custom_properties')
        active_slot = field.get_active_assignment_slot(self.context)
        for slot in [active_slot, field.default_slot]:
            if slot not in custom_properties:
                continue

            definition = PropertySheetSchemaStorage().query(slot)
            if not definition:
                continue

            for solr_field in definition.get_solr_dynamic_fields():
                name = solr_field.name
                if name in custom_properties[slot]:
                    value = solr_field.convert_value(custom_properties[slot][name])
                    data[solr_field.solr_field_name] = value
        return data


class DossierIndexHandler(CustomPropertiesIndexHandler):

    behavior = IDossierCustomProperties


class DocumentIndexHandler(CustomPropertiesIndexHandler, DexterityItemIndexHandler):

    behavior = IDocumentCustomProperties

    def get_data(self, attributes):
        data = super(DocumentIndexHandler, self).get_data(attributes)
        # DexterityItems request excplicitly all attributes without
        # SearchableText when no attributes are specified for indexing.
        # If this is the case, we need to add the custom properties.
        if attributes:
            all_fields = self.all_indexable_fields()
            if set(attributes) | set([u'SearchableText']) == all_fields:
                data.update(self.get_custom_properties())
        return data
