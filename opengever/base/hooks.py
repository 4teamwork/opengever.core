from opengever.base import model
from opengever.base.config import INDEXES
from opengever.core.catalog import add_catalog_indexes
from Products.CMFCore.utils import getToolByName
import logging


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


def installed(site):
    remove_standard_extedit_action(site)
    add_catalog_indexes(INDEXES, logging.getLogger('opengever.base'))
    create_models()
