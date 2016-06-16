from opengever.base.sentry import log_msg_to_sentry
from Products.PortalTransforms.transforms.safe_html import SafeHTML
from zope.globalrequest import getRequest


# These are the HTML tags that are supported by trix
VALID_TAGS = {
    'b'          : 1,
    'br'         : 0,
    'div'        : 1,
    'em'         : 1,
    'i'          : 1,
    'li'         : 1,
    'ol'         : 1,
    'p'          : 1,
    'strong'     : 1,
    'u'          : 1,
    'ul'         : 1,
}

# we invent our own mime-types here to avoid that this transform is used
# instead of the safe_html transform
TRIX_HTML_MIME_TYPE = 'text/x-html-trix'
SABLON_HTML_MIME_TYPE = 'text/x-html-sablon'


class TrixToSablon(SafeHTML):

    __name__ = 'trix_to_sablon'
    inputs = (TRIX_HTML_MIME_TYPE, )
    output = SABLON_HTML_MIME_TYPE

    def _log_unexpected_conversion_to_sentry(self, data, orig):
        request = getRequest()

        extra = {
            'converted_html': data,
            'source_html': orig
        }

        log_msg_to_sentry(
            'Unexpected html during trix/sablon conversion',
            request=request,
            url=request.get('ACTUAL_URL', ''),
            extra=extra)

    def convert(self, orig, data, **kwargs):
        data = super(TrixToSablon, self).convert(orig, data, **kwargs)
        if data != orig:
            self._log_unexpected_conversion_to_sentry(data, orig)
        return data


# This is basically a copy of the safe_html transform, but we allow only the
# html tags that are supported by sablon/trix.
def register():
    return TrixToSablon(valid_tags=VALID_TAGS)
