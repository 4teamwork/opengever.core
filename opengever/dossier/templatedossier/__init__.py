from opengever.dossier.templatedossier.interfaces import ITemplateDossier
from plone import api


def get_template_dossier():
    catalog = api.portal.get_tool('portal_catalog')
    result = catalog(
        portal_type="opengever.dossier.templatedossier",
        sort_on='path')

    if result:
        return result[0].getObject()
    return None
