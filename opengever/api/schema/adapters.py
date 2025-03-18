from opengever.api.schema.schema import TYPE_TO_BE_ADDED_KEY
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.schema import IIdentifier
from opengever.base.schema import IMultiTypeField
from opengever.base.vocabulary import WrapperBase
from opengever.dossier import is_grant_dossier_manager_to_responsible_enabled
from plone import api
from plone.restapi.types.adapters import ASCIILineJsonSchemaProvider
from plone.restapi.types.adapters import ChoiceJsonSchemaProvider
from plone.restapi.types.adapters import CollectionJsonSchemaProvider
from plone.restapi.types.adapters import DefaultJsonSchemaProvider
from plone.restapi.types.adapters import ListJsonSchemaProvider
from plone.restapi.types.adapters import SetJsonSchemaProvider
from plone.restapi.types.adapters import TupleJsonSchemaProvider
from plone.restapi.types.interfaces import IJsonSchemaProvider
from plone.restapi.types.z3crelationadapter import ChoiceslessRelationListSchemaProvider
from z3c.relationfield.interfaces import IRelationList
from zope import schema
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IList
from zope.schema.interfaces import ISet
from zope.schema.interfaces import ITuple


@adapter(IChoice, Interface, IOpengeverBaseLayer)
@implementer(IJsonSchemaProvider)
class GEVERChoiceJsonSchemaProvider(ChoiceJsonSchemaProvider):
    """Customized ChoiceJsonSchemaProvider that renders schema-intent
    aware URLs when used by the @schema endpoint.
    """

    def additional(self):
        result = super(GEVERChoiceJsonSchemaProvider, self).additional()

        # Get information about parent field so that we can use its name to
        # render URLs to sources on anonymous inner value_type Choice fields
        parent_field = getattr(self, 'parent_field', None)

        # Postprocess the ChoiceJsonSchemaProvider to re-build the vocabulary
        # like URLs with (possibly) schema-intent aware ones.

        if 'source' in result:
            result['source']['@id'] = get_source_url(self.field, self.context, self.request,
                                                     parent_field=parent_field)

        if 'querysource' in result:
            result['querysource']['@id'] = get_querysource_url(self.field, self.context, self.request,
                                                               parent_field=parent_field)

        if 'vocabulary' in result:
            vocabulary = getattr(self.field, "vocabulary", None)
            # Handle elephantvocabularies as sources
            if isinstance(vocabulary, WrapperBase):
                result['vocabulary']['@id'] = get_source_url(
                    self.field, self.context, self.request)
            else:
                # Extract vocab_name from URL
                # (it's not always just self.field.vocabularyName)
                vocab_url = result['vocabulary']['@id']
                vocab_name = vocab_url.split('/')[-1]
                result['vocabulary']['@id'] = get_vocabulary_url(vocab_name, self.context, self.request)

        return result


@adapter(IChoice, Interface, IOpengeverBaseLayer)
@implementer(IJsonSchemaProvider)
class DossierResponsibleJsonSchemaProvider(GEVERChoiceJsonSchemaProvider):
    """We specifically overwrite the dossier responsible field serializer to
    include display mode when the user is not allowed to modify the dossier
    responsible.
    """
    def additional(self):
        result = super(DossierResponsibleJsonSchemaProvider, self).additional()
        if is_grant_dossier_manager_to_responsible_enabled() and\
           not IAnnotations(self.request).get(TYPE_TO_BE_ADDED_KEY) and\
           not api.user.has_permission("opengever.dossier: Protect dossier", obj=self.context):
            result['mode'] = 'display'
        return result


@adapter(IChoice, Interface, IOpengeverBaseLayer)
@implementer(IJsonSchemaProvider)
class DossierManagerJsonSchemaProvider(GEVERChoiceJsonSchemaProvider):
    """Use the widgets "display"-mode for dossier_manager field
    if we auto-assign the responsible as dossier manager.
    """
    def additional(self):
        result = super(DossierManagerJsonSchemaProvider, self).additional()
        if is_grant_dossier_manager_to_responsible_enabled():
            result['mode'] = 'display'
        return result

# These IJsonSchemaProviders below are customized so that we can retain
# a link to the parent field. We do this so that we can use the parent field's
# name to render URLs to sources on anonymous inner value_type Choice fields.


@adapter(ICollection, Interface, IOpengeverBaseLayer)
@implementer(IJsonSchemaProvider)
class GEVERCollectionJsonSchemaProvider(CollectionJsonSchemaProvider):

    def get_items(self):
        """Get items properties."""
        value_type_adapter = getMultiAdapter(
            (self.field.value_type, self.context, self.request), IJsonSchemaProvider
        )

        # Retain information about parent field
        value_type_adapter.parent_field = self.field
        return value_type_adapter.get_schema()


@adapter(ITuple, Interface, IOpengeverBaseLayer)
@implementer(IJsonSchemaProvider)
class GEVERTupleJsonSchemaProvider(TupleJsonSchemaProvider):

    def get_items(self):
        """Get items properties."""
        value_type_adapter = getMultiAdapter(
            (self.field.value_type, self.context, self.request), IJsonSchemaProvider
        )

        # Retain information about parent field
        value_type_adapter.parent_field = self.field
        return value_type_adapter.get_schema()


@adapter(ISet, Interface, IOpengeverBaseLayer)
@implementer(IJsonSchemaProvider)
class GEVERSetJsonSchemaProvider(SetJsonSchemaProvider):

    def get_items(self):
        """Get items properties."""
        value_type_adapter = getMultiAdapter(
            (self.field.value_type, self.context, self.request), IJsonSchemaProvider
        )

        # Retain information about parent field
        value_type_adapter.parent_field = self.field
        return value_type_adapter.get_schema()


@adapter(IList, Interface, IOpengeverBaseLayer)
@implementer(IJsonSchemaProvider)
class GEVERListJsonSchemaProvider(ListJsonSchemaProvider):

    def get_items(self):
        """Get items properties."""
        value_type_adapter = getMultiAdapter(
            (self.field.value_type, self.context, self.request), IJsonSchemaProvider
        )

        # Retain information about parent field
        value_type_adapter.parent_field = self.field
        return value_type_adapter.get_schema()


@adapter(IRelationList, Interface, IOpengeverBaseLayer)
@implementer(IJsonSchemaProvider)
class GEVERChoiceslessRelationListSchemaProvider(ChoiceslessRelationListSchemaProvider):
    def get_items(self):
        """Get items properties."""
        value_type_adapter = getMultiAdapter(
            (self.field.value_type, self.context, self.request), IJsonSchemaProvider
        )

        # Prevent rendering all choices.
        value_type_adapter.should_render_choices = False

        # Retain information about parent field
        value_type_adapter.parent_field = self.field

        return value_type_adapter.get_schema()


def get_vocab_like_url(endpoint, locator, context, request):
    """Construct a schema-intent aware URL to a vocabulary-like endpoint.

    (@vocabularies, @sources or @querysources)

    The `locator` is, dependent on the endpoint, either the vocabulary name
    or a field name.

    If a TYPE_TO_BE_ADDED_KEY is present in the request annotation, this
    signals add-intent and will be used as the portal_type of the object
    to be added.

    If TYPE_TO_BE_ADDED_KEY is missing from request annotations, edit-intent
    will be assumed.
    """
    portal_type = IAnnotations(request).get(TYPE_TO_BE_ADDED_KEY)

    try:
        context_url = context.absolute_url()
    except AttributeError:
        portal = getSite()
        context_url = portal.absolute_url()

    if portal_type is None:
        # edit - context is the object to be edited
        url = '/'.join((context_url, endpoint, locator))
    else:
        # add - context is the container where the obj will be added
        url = '/'.join((context_url, endpoint, portal_type, locator))

    return url


def get_vocabulary_url(vocab_name, context, request, portal_type=None):
    return get_vocab_like_url('@vocabularies', vocab_name, context, request)


def get_querysource_url(field, context, request, portal_type=None, parent_field=None):
    field_name = field.getName()
    if parent_field:
        # If we're getting passed a parent_field, we assume that our actual
        # field is an anonymous inner Choice field that's being used as the
        # value_type for the multivalued parent_field. In that case, we omit
        # the inner field's empty string name from the URL, and instead
        # construct an URL that points to the parent field.
        field_name = parent_field.getName()

    return get_vocab_like_url('@querysources', field_name, context, request)


def get_source_url(field, context, request, portal_type=None, parent_field=None):
    field_name = field.getName()
    if parent_field:
        # If we're getting passed a parent_field, we assume that our actual
        # field is an anonymous inner Choice field that's being used as the
        # value_type for the multivalued parent_field. In that case, we omit
        # the inner field's empty string name from the URL, and instead
        # construct an URL that points to the parent field.
        field_name = parent_field.getName()

    return get_vocab_like_url('@sources', field_name, context, request)


@adapter(IMultiTypeField, Interface, Interface)
@implementer(IJsonSchemaProvider)
class GEVERMultiTypeFieldJsonSchemaProvider(DefaultJsonSchemaProvider):

    JSON_SCHEMA_TYPES = {
        schema.TextLine.__name__: 'string',
        schema.Text.__name__: 'string',
        schema.Int.__name__: 'integer',
        schema.Bool.__name__: 'boolean',
        schema.Date.__name__: 'string',
        schema.List.__name__: 'array',
        schema.Set.__name__: 'array',
    }

    def get_type(self):
        types = [
            self.JSON_SCHEMA_TYPES[t.__name__]
            for t in self.field.allowed_types
        ]
        return list(set(types))

    def get_factory(self):
        return None


@adapter(IIdentifier, Interface, Interface)
@implementer(IJsonSchemaProvider)
class GEVERIdentifierJsonSchemaProvider(ASCIILineJsonSchemaProvider):

    def additional(self):
        data = super(GEVERIdentifierJsonSchemaProvider, self).additional()
        data.update({'pattern': self.field.pattern})
        return data

    def get_factory(self):
        return 'string'
