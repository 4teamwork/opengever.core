from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldDeserializer
from z3c.form.interfaces import IManagerValidator
from z3c.form.interfaces import IValidator
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import Attribute
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import Invalid
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema import getFields
from zope.schema.interfaces import ValidationError


class ITransitionExtender(Interface):
    """Interface for adapters, to extend a specific worklow transition,
    with additional required attributes and fuctionality.
    """

    schemas = Attribute(
        "A list of zope schemas, to define additional transition parameters.")

    def after_transition_hook(transition, disable_sync, transition_params):
        """Method which is called after the regular workflow transition (state change),
        to run additional functionality.
        """

    def deserialize(transition_params):
        """Method which deserialize and validate transition paramters according
        to the fields defined in the schemas attribute.
        """


@implementer(ITransitionExtender)
@adapter(IDexterityContent, IBrowserRequest)
class TransitionExtender(object):

    schemas = []

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def after_transition_hook(self, transition, disable_sync, transition_params):
        pass

    def validate_schema(self, transition_params):
        """Validates the schema and collect the erros.
        """
        values, errors = self._deserialize_values(transition_params,
                                                 collect_errors=True)
        return errors

    def deserialize(self, transition_params):
        values, errors = self._deserialize_values(transition_params)
        return values

    def _deserialize_values(self, transition_params, collect_errors=False):
        """Deserialize and validates the defined schema returns a values and
        a list of errors.
        """
        errors = []
        values = {}

        for schema in self.schemas:
            schema_data, deserialize_errors = self._deserialize_schema(schema, transition_params, collect_errors)
            errors.extend(deserialize_errors)
            values.update(schema_data)

        return values, errors

    def _validate_schema(self, schema, schema_data, collect_errors=False):
        errors = []
        validator = queryMultiAdapter(
            (self.context, getRequest(), None, schema, None),
            IManagerValidator)

        for error in validator.validate(schema_data):
            if not collect_errors:
                raise ValueError(error.message)

            errors.append({'error': error, 'message': error.message})
        return errors

    def _deserialize_schema(self, schema, transition_params, collect_errors=False):
        field_data = {}
        errors = []
        for name, field in getFields(schema).items():
            if name in transition_params:
                # Deserialize to field value
                deserializer = queryMultiAdapter(
                    (field, self.context, getRequest()), IFieldDeserializer)
                if deserializer is None:
                    continue

                try:
                    value = deserializer(transition_params[name])
                    validator = queryMultiAdapter(
                        (self.context, self.request, None, field, None), IValidator)
                    if validator:
                        validator.validate(value)

                except (ValueError, Invalid) as e:
                    if not collect_errors:
                        raise
                    errors.append({'message': e.message, 'field': name, 'error': e})

                except ValidationError as e:
                    if not collect_errors:
                        raise
                    errors.append({'message': e.doc(), 'field': name, 'error': e})
                else:
                    field_data[name] = value

            else:
                field_data[name] = field.missing_value

                try:
                    field.validate(field_data.get(name))
                except ValidationError as e:
                    if not collect_errors:
                        raise
                    errors.append({'message': e.doc(), 'field': name, 'error': e})

        errors.extend(self._validate_schema(schema, field_data))
        return field_data, errors
