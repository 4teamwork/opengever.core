from opengever.dossier.templatefolder.interfaces import ITemplateFolder  # keep!
from opengever.dossier.templatefolder.templatefolder import TemplateFolder  # keep!
from plone import api


__all__ = ['ITemplateFolder', 'TemplateFolder', 'get_template_folder']


def get_template_folder():
    catalog = api.portal.get_tool('portal_catalog')
    result = catalog(
        portal_type="opengever.dossier.templatefolder",
        sort_on='path')

    if result:
        return result[0].getObject()
    return None
