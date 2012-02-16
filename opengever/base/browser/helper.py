from opengever.ogds.base.interfaces import IContactInformation
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility


def client_title_helper(item, value):
    """Returns the client title out of the client id (`value`).
    """
    if not value:
        return value

    info = getUtility(IContactInformation)
    client = info.get_client_by_id(value)

    if client:
        return client.title

    else:
        return value


def css_class_from_brain(item):
    normalize = getUtility(IIDNormalizer).normalize
    if not item.portal_type == 'opengever.document.document':
        css_class = "contenttype-%s" % normalize(item.portal_type)
    else:
        # It's a document, we therefore want to display an icon
        # for the mime type of the contained file
        icon = getattr(item, 'getIcon', '')
        if not icon == '':
            # Strip '.gif' from end of icon name and remove leading 'icon_'
            filetype = icon[:icon.rfind('.')].replace('icon_', '')
            css_class = 'icon-%s' % normalize(filetype)
        else:
            # Fallback for unknown file type
            css_class = "contenttype-%s" % normalize(item.portal_type)
    return css_class

def css_class_from_obj(item):
    normalize = getUtility(IIDNormalizer).normalize
    if not item.portal_type == 'opengever.document.document':
        css_class = "contenttype-%s" % normalize(item.portal_type)
    else:
        # XXX: We need to merge this and the css_class_from_brain-method
        # and clean up all packages because we have redundant code.
        if hasattr(item, '_v__is_relation'):
            # Document was listed as a relation, so we use a special icon.
            css_class = "icon-dokument_verweis"
        else:
            # It's a document, we therefore want to display an icon
            # for the mime type of the contained file
            icon = item.getIcon()
            if not icon == '':
                # Strip '.gif' from end of icon name and remove leading 'icon_'
                filetype = icon[:icon.rfind('.')].replace('icon_', '')
                css_class = 'icon-%s' % normalize(filetype)
            else:
                # Fallback for unknown file type
                css_class = "contenttype-%s" % normalize(item.portal_type)
    return css_class
