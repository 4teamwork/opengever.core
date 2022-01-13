from opengever.propertysheets.metaschema import IPropertySheetDefinition
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class PropertySheetLocator(Service):
    """Locates a propertysheet definition by its sheet_id.

    This is a Service base class for all services that need to look up a
    propertysheet definition via a /@propertysheets/{sheet_id} style URL.

    It handles
    - extraction of the {sheet_id} path parameter
    - error response for incorrect number of path parameters
    - validation of {sheet_id}
    - return of a 404 Not Found response if that sheet doesn't exist
    - retrieval of the respective sheet
    in a single place so that not every service has to implement this again,
    and we ensure consistent behavior across all services.

    Because the GET service supports both individual retrieval as well as
    listing, this needs to be handled here as well.
    """

    def __init__(self, context, request):
        super(PropertySheetLocator, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, sheet_id):
        # Consume any path segments after /@propertysheets as parameters
        self.params.append(sheet_id)
        return self

    def get_sheet_id(self):
        sheet_id_required = getattr(self, 'sheet_id_required')

        if sheet_id_required:
            if len(self.params) != 1:
                raise BadRequest(
                    'Must supply exactly one {sheet_id} path parameter.')
        else:
            # We'll accept zero (listing) or one (get by id) params, but not more
            if len(self.params) > 1:
                raise BadRequest(
                    'Must supply either exactly one {sheet_id} path parameter '
                    'to fetch a specific property sheet, or no parameter for a '
                    'listing of all property sheets.')

        # We have a valid number of parameters for the given endpoint
        if len(self.params) == 1:
            sheet_id = self.params[0]
            id_field = IPropertySheetDefinition['id']
            try:
                id_field.bind(sheet_id).validate(sheet_id)
            except Exception:
                raise BadRequest(u"The name '{}' is invalid.".format(sheet_id))

            return sheet_id

    def locate_sheet(self):
        sheet_id = self.get_sheet_id()

        if sheet_id is not None:
            storage = PropertySheetSchemaStorage()
            definition = storage.get(sheet_id)

            if not definition:
                raise NotFound

            return definition
