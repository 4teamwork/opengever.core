import json

from plone import api
from plone.app.theming.interfaces import IThemeSettings
from plone.registry.interfaces import IRegistry
from plonetheme.teamraum.hooks import SCREEN_ANNOTATION_KEY
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility

from plonetheme.teamraum.importexport import CustomStylesUtility


def import_styles_configuration(context):
    """ This importstep checks if there is a specific json
    file and imports it into the theme customstyles.
    """

    styles = context.readDataFile('customstyles.json')

    if styles is None:
        return

    data = json.loads(styles)

    site = context.getSite()

    customstyles_util = CustomStylesUtility(site)

    # reset styles if there is nothing in annotations
    if 'customstyles' not in customstyles_util.annotations:
        customstyles_util.reset_styles()

    customstyles_util.import_styles(data)


def import_various(context):
    """Import step for configuration and uninstallation that is not handled
    in xml files.

    You need to place a marker file in the profiles directory where you want
    to hook in. This file should contain one word which will be used to
    determine which code to be executed (configuration, uninstallation, etc.).

    """
    action = context.readDataFile('plonetheme.teamraum.setuphandlers.txt')

    if action is None:
        return

    action = action.strip()

    if action == 'uninstall':
        registry = getUtility(IRegistry)

        settings = registry.forInterface(IThemeSettings)

        # Revert changes of the app registry.
        settings.doctype = ''
        settings.currentTheme = u''
        settings.enabled = False
        settings.readNetwork = False
        settings.parameterExpressions.pop('navisearch')
        settings.rules = u''
        settings.absolutePrefix = u''

        # Revert changes from "controlpanel.xml".
        config_tool = api.portal.get_tool('portal_controlpanel')
        config_tool.unregisterConfiglet('plonetheme.teamraum')

        # Restore 'screen' media types.
        restore_screen_media_types(context.getSite())


def restore_screen_media_types(site):
    """ Restores 'screen' media types removed in hooks.py.
    """
    annotations = IAnnotations(site)
    config = annotations[SCREEN_ANNOTATION_KEY]

    csstool = getToolByName(site, 'portal_css')

    for sheet_id in config:
        sheet = csstool.getResource(sheet_id)
        if sheet and not sheet.getMedia():
            csstool.updateStylesheet(sheet_id, media='screen')
