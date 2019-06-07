from opengever.core.catalog import add_catalog_indexes
from opengever.document.config import INDEXES
from opengever.document.modifiers import modifiers
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.interfaces.IModifier import IConditionalTalesModifier
import logging


def installed(site):
    add_catalog_indexes(INDEXES, logging.getLogger('opengever.document'))
    install_modifiers(site)


def install_modifiers(site):
    portal_modifier = getToolByName(site, 'portal_modifier')
    for m in modifiers:
        id_ = m['id']
        if id_ in portal_modifier.objectIds():
            continue
        title = m['title']
        modifier = m['modifier'](id_, title)
        wrapper = m['wrapper'](id_, modifier, title)
        enabled = m['enabled']
        if IConditionalTalesModifier.providedBy(wrapper):
            wrapper.edit(enabled, m['condition'])
        else:
            wrapper.edit(enabled)
        portal_modifier.register(m['id'], wrapper)
