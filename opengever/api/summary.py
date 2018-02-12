from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.utils import get_preferred_language_code
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.summary import DefaultJSONSummarySerializer
from plone.rfc822.interfaces import IPrimaryFieldInfo
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

        obj = IContentListingObject(self.context)
        summary = json_compatible({
            '@id': obj.getURL(),
        })

        for field in field_list:
            accessor = FIELD_ACCESSORS.get(field)
            if accessor is None:
                continue
            if isinstance(accessor, str):
                value = getattr(obj, accessor, None)
                if callable(value):
                    value = value()
            else:
                value = accessor(obj)
            summary[field] = json_compatible(value)

        if ('title' in summary and
                ITranslatedTitleSupport.providedBy(self.context)):
            # Update title to contain translated title in negotiated language
            attr = 'title_{}'.format(get_preferred_language_code())
            summary['title'] = getattr(self.context, attr)

        return summary


def filesize(obj):
    try:
        info = IPrimaryFieldInfo(obj.getObject())
    except TypeError:
        return 0
    if info.value is None:
        return 0
    return info.value.size


def filename(obj):
    try:
        info = IPrimaryFieldInfo(obj.getObject())
    except TypeError:
        return None
    if info.value is None:
        return None
    return info.value.filename


FIELD_ACCESSORS = {
    '@type': 'PortalType',
    'created': 'created',
    'creator': 'Creator',
    'description': 'Description',
    'filename': filename,
    'filesize': filesize,
    'mimetype': 'getContentType',
    'modified': 'modified',
    'review_state': 'review_state',
    'title': 'Title',
}
