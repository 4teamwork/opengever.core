from opengever.api.schema.schema import TYPE_TO_BE_ADDED_KEY
from opengever.base.interfaces import IOpengeverBaseLayer
from plone.restapi.types.adapters import ChoiceJsonSchemaProvider
from plone.restapi.types.interfaces import IJsonSchemaProvider
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IChoice


@adapter(IChoice, Interface, IOpengeverBaseLayer)
@implementer(IJsonSchemaProvider)
class GEVERChoiceJsonSchemaProvider(ChoiceJsonSchemaProvider):
    """Customized ChoiceJsonSchemaProvider that renders schema-intent
    aware URLs when used by the @schema endpoint.
    """

    def additional(self):
        result = super(GEVERChoiceJsonSchemaProvider, self).additional()

        # Postprocess the ChoiceJsonSchemaProvider to re-build the vocabulary
        # like URLs with (possibly) schema-intent aware ones.

        if 'source' in result:
            result['source']['@id'] = get_source_url(self.field, self.context, self.request)

        if 'querysource' in result:
            result['querysource']['@id'] = get_querysource_url(self.field, self.context, self.request)

        if 'vocabulary' in result:
            # Extract vocab_name from URL
            # (it's not always just self.field.vocabularyName)
            vocab_url = result['vocabulary']['@id']
            vocab_name = vocab_url.split('/')[-1]
            result['vocabulary']['@id'] = get_vocabulary_url(vocab_name, self.context, self.request)

        return result


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


def get_querysource_url(field, context, request, portal_type=None):
    return get_vocab_like_url('@querysources', field.getName(), context, request)


def get_source_url(field, context, request, portal_type=None):
    return get_vocab_like_url('@sources', field.getName(), context, request)
