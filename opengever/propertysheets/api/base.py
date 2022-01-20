from opengever.api.validation import get_validation_errors
from opengever.api.validation import scrub_json_payload
from opengever.propertysheets.api.error_serialization import ErrorSerializer
from opengever.propertysheets.definition import PropertySheetSchemaDefinition as PSDefinition
from opengever.propertysheets.exceptions import AssignmentAlreadyInUse
from opengever.propertysheets.exceptions import SheetValidationError
from opengever.propertysheets.metaschema import IFieldDefinition
from opengever.propertysheets.metaschema import IPropertySheetDefinition
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


class PropertySheetAPIBase(object):
    """Base class for @propertysheets API endpoints.
    """

    @property
    def storage(self):
        return PropertySheetSchemaStorage()

    def serialize(self, sheet_definition):
        serializer = getMultiAdapter(
            (sheet_definition, self.request),
            ISerializeToJson,
        )
        return serializer()

    def serialize_exception(self, exc):
        return ErrorSerializer(exc, self.request)()


@implementer(IPublishTraverse)
class PropertySheetLocator(PropertySheetAPIBase, Service):
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
            except Exception as exc:
                errors = [('id', exc)]
                raise SheetValidationError(errors)

            return sheet_id

    def locate_sheet(self):
        sheet_id = self.get_sheet_id()

        if sheet_id is not None:
            storage = PropertySheetSchemaStorage()
            definition = storage.get(sheet_id)

            if not definition:
                raise NotFound

            return definition


class PropertySheetWriter(PropertySheetLocator):
    """Base class for @propertysheets endpoints that create or modify sheets.
    """

    def validate_fields(self, fields, existing_dynamic_defaults=()):
        errors = []

        for field_no, field_data in enumerate(fields):
            # Cast JSON strings to their appropriate Python types (unicode or
            # bytestring), depending on the schema field (ASCII or Text[Line])
            scrub_json_payload(field_data, IFieldDefinition)

            # Allowing unknown fields is necessary in order to allow managers
            # to set dynamic defaults like `default_factory`, which currently
            # aren't exposed in the meta schema.
            field_errors = get_validation_errors(
                field_data, IFieldDefinition, allow_unknown_fields=True)

            for field_error in field_errors:
                # Keep track of position and name of propertysheet fields
                errors.append((
                    field_no,
                    field_data.get('name'),
                    field_error,
                ))

            self.validate_dynamic_defaults(field_data, existing_dynamic_defaults)

        return errors

    def validate_dynamic_defaults(self, field_data, existing_dynamic_defaults):
        """Require Manager role for any kind of dynamic defaults, unless
        it's a PATCH request and they already existed and didn't get modified.
        """
        dynamic_default_types = PSDefinition.DYNAMIC_DEFAULT_PROPERTIES

        for name, value in field_data.items():
            if name not in dynamic_default_types:
                continue
            if (field_data['name'], name, value) in existing_dynamic_defaults:
                # Existing dynamic default that is left unchanged - allowed
                continue
            else:
                # New or modified dynamic default - managers only
                if not api.user.has_permission('cmf.ManagePortal'):
                    raise Unauthorized(
                        'Setting any dynamic defaults requires Manager role')

    def validate_assignments(self, assignments_data):
        if not assignments_data:
            return

        errors = []

        # Validate field data
        assignments_field = IPropertySheetDefinition['assignments']
        try:
            assignments_field.bind(assignments_data).validate(assignments_data)
        except Exception as exc:
            errors.append(exc)

        # Validate that assignment isn't already in use
        storage = IAnnotations(self.storage.context).get(
            self.storage.ANNOTATIONS_KEY, {})
        used_assignments = {}
        for sheet_id, definition_data in storage.items():
            for assignment in definition_data['assignments']:
                used_assignments[assignment] = sheet_id

        for new_assignment in assignments_data:
            in_use_by = used_assignments.get(new_assignment)
            if in_use_by:
                exc = AssignmentAlreadyInUse({
                    'assignment': new_assignment,
                    'in_use_by': in_use_by,
                })
                errors.append(exc)

        return errors

    def create_property_sheet(self, sheet_id, assignments, fields):
        schema_definition = PSDefinition.create(
            sheet_id,
            assignments=assignments,
        )

        for field_data in fields:

            name = field_data['name']
            field_type = field_data['field_type']
            title = field_data.get('title', name.decode('ascii'))
            description = field_data.get('description', u'')
            required = field_data.get('required', False)

            kwargs = {
                'values': field_data.get('values'),
                'default': field_data.get('default'),
                'default_factory': field_data.get('default_factory'),
                'default_expression': field_data.get('default_expression'),
                'default_from_member': field_data.get('default_from_member'),
            }

            schema_definition.add_field(
                field_type, name, title, description, required,
                **kwargs
            )

        self.storage.save(schema_definition)
        return self.storage.get(sheet_id)
