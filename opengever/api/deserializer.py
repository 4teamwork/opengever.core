from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.default_values import set_default_values
from opengever.base.interfaces import IOpengeverBaseLayer
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.dxcontent import DeserializeFromJson
from plone.restapi.interfaces import IDeserializeFromJson
from z3c.form.interfaces import IManagerValidator
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectModifiedEvent


@implementer(IDeserializeFromJson)
@adapter(IDexterityContent, IOpengeverBaseLayer)
class GeverDeserializeFromJson(DeserializeFromJson):
    """Customization of the default deserializer, to return the message
    factory object instead of the error message string, if a validation error
    occurs.
    It also makes sure to prefill values that were not set with default or
    missing values.
    """

    def __call__(self, validate_all=False, data=None, create=False):

        if data is None:
            data = json_body(self.request)

        # set default values
        if create:
            container = aq_parent(aq_inner(self.context))
            set_default_values(self.context, container, data)

        schema_data, errors = self.get_schema_data(data, validate_all)

        # Validate schemata
        for schema, field_data in schema_data.items():
            validator = queryMultiAdapter(
                (self.context, self.request, None, schema, None), IManagerValidator
            )
            for error in validator.validate(field_data):
                errors.append({"error": error, "message": error.message})

        if errors:
            # Drop Python specific error classes in order to be able to better handle
            # errors on front-end
            for error in errors:
                error["error"] = "ValidationError"

            raise BadRequest(errors)

        # We'll set the layout after the validation and even if there
        # are no other changes.
        if "layout" in data:
            layout = data["layout"]
            self.context.setLayout(layout)

        # OrderingMixin
        self.handle_ordering(data)

        if self.modified and not create:
            descriptions = []
            for interface, names in self.modified.items():
                descriptions.append(Attributes(interface, *names))
            notify(ObjectModifiedEvent(self.context, *descriptions))

        return self.context
