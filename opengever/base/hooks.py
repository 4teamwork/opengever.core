from opengever.base import model
from opengever.base.transforms import trix_html_to_sablon_html
from plone import api
from Products.CMFCore.utils import getToolByName


DEFAULT_EXTEDIT_ACTION_IDENTIFIER = 'extedit'


def remove_action_from_category(context, category, action_id):
    """Remove the action identified by ``action_id`` from
    the CMF action category identified by ``category``.
    """
    pa = getToolByName(context, 'portal_actions')

    cat = pa.get(category)
    if cat and action_id in cat:
        del cat[action_id]


def remove_standard_extedit_action(context):
    """Remove the ``extedit`` action (Products.CMFPlone) from document_actions.
    """
    remove_action_from_category(context, 'document_actions',
                                DEFAULT_EXTEDIT_ACTION_IDENTIFIER)


def create_models():
    model.Base.metadata.create_all(model.Session().bind, checkfirst=True)


def register_trix_to_sablon_transform():
    types_tool = api.portal.get_tool('portal_transforms')
    types_tool.registerTransform(trix_html_to_sablon_html.register())


def installed(site):
    remove_standard_extedit_action(site)
    create_models()
    register_trix_to_sablon_transform()
