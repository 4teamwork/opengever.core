from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.utils import get_preferred_language_code
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.summary import DefaultJSONSummarySerializer
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJsonSummary)
@adapter(Interface, IOpengeverBaseLayer)
class GeverJSONSummarySerializer(DefaultJSONSummarySerializer):
    """Customized ISerializeToJsonSummary adapter for GEVER.

    Includes
    - translated 'title' for objects with ITranslatedTitleSupport
    - the object's portal_type
    - the possibility to register a custom serializer per type

    Titles will be translated in the negotiated language, coming from the
    request's Accept-Language header for API requests.

    Note: Because we have combined language codes enabled in the
    portal_languages tool, language codes sent in the Accept-Language header
    need to be written in the combined form (e.g., 'de-ch') for language
    content negotiation to work properly.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        # Get the default summary first, then modify it as needed
        summary = super(GeverJSONSummarySerializer, self).__call__()

        # Include portal_type
        summary['@type'] = self.context.portal_type

        if ITranslatedTitleSupport.providedBy(self.context):
            # Update title to contain translated title in negotiated language
            attr = 'title_{}'.format(get_preferred_language_code())
            summary['title'] = getattr(self.context, attr)

        custom_serializer = queryMultiAdapter((self.context, self.request),
                                              ISerializeToJsonSummary,
                                              name=self.context.portal_type)
        if custom_serializer:
            return custom_serializer()
        else:
            return summary
