from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations

SCREEN_ANNOTATION_KEY = "plonetheme.teamraum.originalmediatypesconfiguration"


def remove_screen_media_types(site):
    """ This function removes the 'screen' media type from the currently
        installed css resources. This way the css resources will also be
        delivered for other media types, e.g. "print".

        Saves original configuration in annotations. Restore function
        is in setuphandlers.py
    """
    annotations = IAnnotations(site)
    if SCREEN_ANNOTATION_KEY not in annotations:
        annotations[SCREEN_ANNOTATION_KEY] = set()

    config = annotations[SCREEN_ANNOTATION_KEY]

    csstool = getToolByName(site, 'portal_css')
    for sheet in csstool.getResources():
        if sheet.getMedia() and sheet.getMedia().lower() == 'screen':
            # save for restore on uninstall
            config.add(sheet.getId())

            csstool.updateStylesheet(sheet.getId(), media='')
