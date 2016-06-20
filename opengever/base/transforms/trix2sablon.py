from opengever.base.sentry import log_msg_to_sentry
from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.transforms.safe_html import SafeHTML
from zope.globalrequest import getRequest


# These are the HTML tags that are supported by sablon
# Value is 1 if they have a closing part (e.g. <p>...</p>) and 0 for empty
# tags (like <br />).
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


_transform = SafeHTML(name='trix_to_sablon', valid_tags=VALID_TAGS)


def convert(markup):
    """Use this function to transform markup from trix to markup that can
    be processed by sablon.

    This converter is expected to do nothing since trix markup is already valid
    for sablon. It is just a safeguard against malicious markup injection or
    against changes in trix.

    Thus we also log to sentry whenever we actually have to convert markup.

    """
    data = _transform.convert(markup, data=datastream('trix_to_sablon'))
    converted = data.getData()
    if converted != markup:
        _log_unexpected_conversion_to_sentry(converted, markup)
    return converted


def _log_unexpected_conversion_to_sentry(converted, markup):
    request = getRequest()

    extra = {
        'converted_html': converted,
        'source_html': markup
    }

    log_msg_to_sentry(
        'Unexpected html during trix/sablon conversion',
        request=request,
        url=request.get('ACTUAL_URL', ''),
        extra=extra)
