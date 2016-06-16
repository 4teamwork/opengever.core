from Products.PortalTransforms.transforms.safe_html import SafeHTML


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


# This is basically a copy of the safe_html transform, but we allow only the
# html tags that are supported by sablon/trix.
def register():
    return SafeHTML(name='trix_to_sablon',
                    inputs=(TRIX_HTML_MIME_TYPE, ),
                    output=SABLON_HTML_MIME_TYPE,
                    valid_tags=VALID_TAGS)
