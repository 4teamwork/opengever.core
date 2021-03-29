from ftw.solr.handlers import DefaultIndexHandler
from ftw.solr.handlers import DexterityItemIndexHandler
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.dossier.behaviors.customproperties import IDossierCustomProperties
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from zope.schema import getFields
from zope.schema import Text


SOLR_TYPES = {
    'unicode': 'string',
    'str': 'string',
    'bool': 'boolean',
    'int': 'int',
}


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

        custom_properties = adapted.custom_properties
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

            for name, custom_field in definition.get_fields():
                # Custom properties are indexed for filtering and sorting.
                # This doesn't make sense for multiline text.
                if type(custom_field) == Text:
                    continue
                if name in custom_properties[slot]:
                    value = custom_properties[slot][name]
                    solr_type = SOLR_TYPES.get(type(value).__name__, 'string')
                    data['{}_custom_field_{}'.format(name, solr_type)] = value

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
            all_fields = set(self.manager.schema.fields.keys())
            if set(attributes) | set([u'SearchableText']) == all_fields:
                data.update(self.get_custom_properties())
        return data
