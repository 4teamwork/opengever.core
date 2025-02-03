from opengever.propertysheets.assignment import get_document_assignment_slots
from opengever.propertysheets.assignment import get_dossier_assignment_slots
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone.restapi.services import Service


LISTING_TO_SLOTS = {
    u'dossiers': get_dossier_assignment_slots,
    u'documents': get_document_assignment_slots,
    u'folder_contents': get_document_assignment_slots,
}


class ListingCustomFieldsGet(Service):
    """API Endpoint which returns custom fields available for listings.

    It returns a nested data structure with custom fields for each supported
    listing, if available.
    Custom fields are provided as follows:
    - Custom field source are property sheets registerd for a type associated
      with a listing
    - Custom fields must be indexed in solr (i.e. everything but `Text`)
    - If different sheets for the same type index to the same field, only the
      last field is returned.

    GET /@listing-custom-fields HTTP/1.1
    """

    def reply(self):
        solr_fields = {}

        storage = PropertySheetSchemaStorage()
        if not storage:
            return solr_fields

        for listing_name, slot_provider in LISTING_TO_SLOTS.items():
            fields_by_listing = {}

            for slot_name in slot_provider():
                definition = storage.query(slot_name)
                if definition is not None:
                    fields_by_listing.update(
                        definition.get_solr_dynamic_field_schema()
                    )

            if fields_by_listing:
                solr_fields[listing_name] = {
                    'properties': fields_by_listing
                }

        return solr_fields
