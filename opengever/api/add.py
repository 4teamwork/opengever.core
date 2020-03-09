# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Acquisition.interfaces import IAcquirer
from opengever.meeting.browser.proposalforms import get_selected_template
from opengever.meeting.browser.proposalforms import IAddProposalSupplementaryFields
from plone.restapi.deserializer import json_body
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from plone.restapi.services.content.utils import add
from plone.restapi.services.content.utils import create
from Products.CMFPlone.utils import safe_hasattr
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface.exceptions import Invalid
from zope.lifecycleevent import ObjectCreatedEvent
from zope.schema import getFieldsInOrder
from zope.schema import ValidationError
from zope.schema.interfaces import RequiredMissing
import plone.protect.interfaces


class FolderPost(Service):
    """Copy of plone.restapi.services.content.add.FolderPost
    but with code split up in different methods.
    """

    @property
    def request_data(self):
        return json_body(self.request)

    def extract_data(self):
        data = self.request_data

        self.type_ = data.get("@type", None)
        self.id_ = data.get("id", None)
        self.title_ = data.get("title", None)

        if not self.type_:
            raise BadRequest("Property '@type' is required")
        return data

    def deserialize_object(self):
        # Acquisition wrap temporarily to satisfy things like vocabularies
        # depending on tools
        temporarily_wrapped = False
        if IAcquirer.providedBy(self.obj) and not safe_hasattr(self.obj, "aq_base"):
            self.obj = self.obj.__of__(self.context)
            temporarily_wrapped = True

        # Update fields
        deserializer = getMultiAdapter((self.obj, self.request), IDeserializeFromJson)
        deserializer(validate_all=True, create=True)

        if temporarily_wrapped:
            self.obj = aq_base(self.obj)

        if not getattr(deserializer, "notifies_create", False):
            notify(ObjectCreatedEvent(self.obj))

    def add_object_to_context(self):
        self.obj = add(self.context, self.obj, rename=not bool(self.id_))

    def serialize_object(self):
        serializer = queryMultiAdapter((self.obj, self.request), ISerializeToJson)

        serialized_obj = serializer()

        # HypermediaBatch can't determine the correct canonical URL for
        # objects that have just been created via POST - so we make sure
        # to set it here
        serialized_obj["@id"] = self.obj.absolute_url()
        return serialized_obj

    def reply(self):
        self.extract_data()

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        try:
            self.obj = create(self.context, self.type_, id_=self.id_, title=self.title_)
        except Unauthorized as exc:
            self.request.response.setStatus(403)
            return dict(error=dict(type="Forbidden", message=str(exc)))
        except BadRequest as exc:
            self.request.response.setStatus(400)
            return dict(error=dict(type="Bad Request", message=str(exc)))

        try:
            self.deserialize_object()
        except ComponentLookupError:
            self.request.response.setStatus(501)
            return dict(
                error=dict(message="Cannot deserialize type {}".format(self.obj.portal_type))
            )
        except DeserializationError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(type="DeserializationError", message=str(e)))

        self.add_object_to_context()

        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", self.obj.absolute_url())

        serialized_obj = self.serialize_object()

        return serialized_obj


class GeverFolderPost(FolderPost):
    """Contains specific treatment for creation of certain portal types
    """

    def extract_data(self):
        data = super(GeverFolderPost, self).extract_data()
        if self.type_ == 'opengever.meeting.proposal':
            data.update(self.extract_additional_data(data, IAddProposalSupplementaryFields))
            self.validate_additional_schema(data, IAddProposalSupplementaryFields)
        self.data = data
        return data

    def extract_additional_data(self, data, schema):
        """ Deserializes the values corresponding to the passed schema found in
        data. Note that validation of the value happens during deserialization.
        """
        for name, field in getFieldsInOrder(schema):
            if name not in data:
                continue
            validation_data = SchemaValidationData(schema, data, self.context)
            deserializer = queryMultiAdapter((field, validation_data, self.request),
                                             IFieldDeserializer)
            value = deserializer(data[name])
            data[name] = value
        return data

    def validate_additional_schema(self, data, schema):
        """This will validate the values in data corresponding to
        the fields from schema, check that all required fields are
        in data, and validate the invariants.
        """
        errors = get_validation_errors(self.context, data, schema)
        if errors:
            raise BadRequest(errors)

    def add_object_to_context(self):
        super(GeverFolderPost, self).add_object_to_context()
        if self.obj.portal_type == 'opengever.meeting.proposal':
            # For proposals we also need to create the proposal document
            data = SchemaValidationData(IAddProposalSupplementaryFields,
                                        self.data,
                                        self.context)
            proposal_template = get_selected_template(data)
            self.obj.create_proposal_document(
                title=self.obj.title_or_id(),
                source_blob=proposal_template.file,
            )

    def deserialize_object(self):
        """Does the same as parent class, but pass in self.data to the deserializer.
        """

        # Acquisition wrap temporarily to satisfy things like vocabularies
        # depending on tools
        temporarily_wrapped = False
        if IAcquirer.providedBy(self.obj) and not safe_hasattr(self.obj, "aq_base"):
            self.obj = self.obj.__of__(self.context)
            temporarily_wrapped = True

        # Update fields
        deserializer = getMultiAdapter((self.obj, self.request), IDeserializeFromJson)
        deserializer(validate_all=True, create=True, data=self.data)

        if temporarily_wrapped:
            self.obj = aq_base(self.obj)

        if not getattr(deserializer, "notifies_create", False):
            notify(ObjectCreatedEvent(self.obj))


class SchemaValidationData(object):
    """To validate a field, it needs to be bound to its context, as for example
    certain vocabularies are context-dependent. In the case of content creation,
    the object does not exist yet and the container is used as context, so we
    need to provide access to the data that will be set on the object being
    created (contained either in data or as default values on the schema).
    For example the ProposalTemplatesForCommitteeVocabulary used for the
    proposal_template field needs access to the predeessor_proposal and
    committee_oguid both stored in data.

    This class therefore wraps the context (container) together with data and
    schema defaults to allow correct validation. This is similar to the
    z3c.form.validator.Data class used during form invariants validation.
    """
    def __init__(self, schema, data, context):
        self.context = context
        self.data = data
        self.schema = schema

    def __getattr__(self, name):
        if name in self.data:
            return self.data.get(name)
        if hasattr(self.context, name):
            return getattr(self.context, name)
        if name in self.schema:
            return self.schema.get(name).default
        return None


def get_schema_validation_errors(context, data, schema):
    """Validate a dict against a schema.

    Return a list of basic schema validation errors (required fields,
    constraints, but doesn't check invariants yet).

    Loosely based on zope.schema.getSchemaValidationErrors, but:

    - Processes fields in schema order
    - Handles dict subscription access instead of object attribute access
    - Respects required / optional fields
    - Raises RequiredMissing instead of SchemaNotFullyImplemented
    """
    validation_data = SchemaValidationData(schema, data, context)
    errors = []
    for name, field in getFieldsInOrder(schema):
        try:
            value = data[name]
        except KeyError:
            # property for the given name is not implemented
            if not field.required:
                continue
            errors.append((name, RequiredMissing(name)))
        else:
            try:
                field.bind(validation_data).validate(value)
            except ValidationError as e:
                errors.append((name, e))

    return errors


def get_validation_errors(context, data, schema):
    """Validate a dict against a schema and invariants.

    Return a list of all validation errors, including invariants.
    Based on zope.schema.getValidationErrors.
    """
    errors = get_schema_validation_errors(context, data, schema)
    if errors:
        return errors

    # Only validate invariants if there were no previous errors. Previous
    # errors could be missing attributes which would most likely make an
    # invariant raise an AttributeError.
    invariant_errors = []
    try:
        schema.validateInvariants(SchemaValidationData(schema, data, context),
                                  invariant_errors)
    except Invalid:
        # Just collect errors
        pass
    errors = [(None, e) for e in invariant_errors]
    return errors
