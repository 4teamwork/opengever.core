from opengever.base import _
from zope.i18n import translate


TRANSLATIONS = (
    _(u'label_add_to_favorites',
        default=u'Add to favorites'),
    _(u'label_remove_from_favorites',
        default=u'Remove from favorites')
    )


def get_translations(request):
    return {
        unicode(message): translate(message, context=request)
        for message in TRANSLATIONS
    }
