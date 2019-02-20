from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldDeserializer
from z3c.form.interfaces import IManagerValidator
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import Attribute
from zope.interface import implementer
from zope.interface import Interface
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
        schema_data = {}
        errors = []
        values = {}

        for schemata in self.schemas:
            for name, field in getFields(schemata).items():
                field_data = schema_data.setdefault(schemata, {})

                if name in transition_params:
                    # Deserialize to field value
                    deserializer = queryMultiAdapter(
                        (field, self.context, getRequest()), IFieldDeserializer)
                    if deserializer is None:
                        continue

                    try:
                        value = deserializer(transition_params[name])
                    except ValueError as e:
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

            values.update(field_data)

        # Validate schemata
        for schemata, field_data in schema_data.items():
            validator = queryMultiAdapter(
                (self.context, getRequest(), None, schemata, None),
                IManagerValidator)
            for error in validator.validate(field_data):
                if not collect_errors:
                    raise ValueError(error.message)

                errors.append({'error': error, 'message': error.message})

        return values, errors
