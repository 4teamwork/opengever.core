from opengever.api.deserializer import GeverDeserializeFromJson
from opengever.api.relationfield import relationfield_value_to_object
from opengever.disposition.disposition import IDispositionSchema
from opengever.disposition.validators import OfferedDossiersValidator
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from zExceptions import BadRequest
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import Invalid


@implementer(IDeserializeFromJson)
@adapter(IDispositionSchema, Interface)
class DeserializeDispositionFromJson(GeverDeserializeFromJson):
    """In order to be able to return translated and speaking error
    messages, we have to manually check the dossier data and raise any errors.
    """

    def __call__(self, validate_all=False, data=None, create=False):
        if data is None:
            data = json_body(self.request)

        # Pre validate selected dossiers to provide specific error message
        # if invalid
        dossiers = []
        field = IDispositionSchema['dossiers']
        for value in data.get('dossiers', []):
            obj, resolved_by = relationfield_value_to_object(
                value, self.context, self.request)
            dossiers.append(obj)

            try:
                validator = OfferedDossiersValidator(
                    self.context, self.request, None, field, None)
                validator.validate(dossiers)
            except Invalid as err:
                raise BadRequest(err.message)

        return super(DeserializeDispositionFromJson, self).__call__(
            validate_all=validate_all, data=data, create=create)
