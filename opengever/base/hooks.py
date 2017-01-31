from opengever.base import model
from opengever.base.indexes import UserTurboIndex
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


def installed(site):
    remove_standard_extedit_action(site)
    create_models()
    install_turbo_indexes(site)


def install_turbo_indexes(site):
    replace_with_turbo_index(site, 'Creator', UserTurboIndex)


def replace_with_turbo_index(site, index_name, index_class):
    catalog = getToolByName(site, 'portal_catalog')
    indexes = catalog._catalog.indexes
    old_index = indexes[index_name]
    if isinstance(old_index, index_class):
        return

    new_index = index_class(old_index.id)
    new_index.__dict__.update(old_index.__dict__)
    indexes[index_name] = new_index
    catalog._catalog._p_changed = True
