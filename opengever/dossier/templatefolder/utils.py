from Acquisition import aq_chain
from opengever.dossier.templatefolder.interfaces import ITemplateFolder


def is_within_templates(context):
    """ Checks, if the content is within the templates.
    """

    return bool(filter(ITemplateFolder.providedBy, aq_chain(context)))
