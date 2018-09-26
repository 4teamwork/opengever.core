from plone.restapi.interfaces import IFieldDeserializer
from z3c.form.interfaces import IManagerValidator
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFields
from zope.schema.interfaces import ValidationError


class ITransitionExtender(Interface):
    """Transition extender interface
    """


@implementer(ITransitionExtender)
@adapter(Interface)
class TransitionExtender(object):

    schemas = []

    def __init__(self, context):
        self.context = context

    def after_transition_hook(self, **kwargs):
        pass

    def deserialize(self, **data):
        validate_all = True
        schema_data = {}
        errors = []
        values = {}

        for schemata in self.schemas:
            for name, field in getFields(schemata).items():
                field_data = schema_data.setdefault(schemata, {})

                if name in data:
                    # Deserialize to field value
                    deserializer = queryMultiAdapter(
                        (field, self.context, getRequest()),
                        IFieldDeserializer)
                    if deserializer is None:
                        continue

                    try:
                        value = deserializer(data[name])
                    except ValueError as e:
                        errors.append({
                            'message': e.message, 'field': name, 'error': e})
                    except ValidationError as e:
                        errors.append({
                            'message': e.doc(), 'field': name, 'error': e})
                    else:
                        field_data[name] = value

                elif validate_all:
                    field_data[name] = field.missing_value

                    try:
                        field.validate(field_data.get(name))
                    except ValidationError as e:
                        errors.append({
                            'message': e.doc(), 'field': name, 'error': e})

            values.update(field_data)

        # Validate schemata
        for schemata, field_data in schema_data.items():
            validator = queryMultiAdapter(
                (self.context, getRequest(), None, schemata, None),
                IManagerValidator)
            for error in validator.validate(field_data):
                errors.append({'error': error, 'message': error.message})

        if errors:
            raise BadRequest(errors)

        return values
