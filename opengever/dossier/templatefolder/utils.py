from Acquisition import aq_chain
from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.dossier.templatefolder.interfaces import ITemplateFolder


def is_within_templates(context):
    """ Checks, if the context is within the templates.
    """

    return bool(filter(ITemplateFolder.providedBy, aq_chain(context)))


def is_directly_within_template_folder(context):
    """ Checks, if the context is directly contained in a template folder.
    """
    parent = aq_parent(aq_inner(context))
    return ITemplateFolder.providedBy(parent)
