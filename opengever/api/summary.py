from opengever.base.interfaces import IOpengeverBaseLayer
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.summary import DefaultJSONSummarySerializer
from opengever.api.listing import create_list_item
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJsonSummary)
@adapter(Interface, IOpengeverBaseLayer)
class GeverJSONSummarySerializer(DefaultJSONSummarySerializer):
    """Customized ISerializeToJsonSummary adapter for GEVER.

    Includes
    - translated 'title' for objects with ITranslatedTitleSupport
    - the object's portal_type
    - custom field list with 'items.fl' query parameter

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
        field_list = self.request.form.get('items.fl', '').strip()
        if field_list:
            field_list = field_list.split(',')
        else:
            field_list = ['@type', 'title', 'description', 'review_state']

        return create_list_item(self.context, field_list)
