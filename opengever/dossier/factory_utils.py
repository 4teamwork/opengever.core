"""
This module contains utility function used by the differents specialdossiers
behaviors' PostFactoryMenu adapters.

"""

from Products.CMFCore.utils import getToolByName


def order_factories(context, factories):
    """Orders the entries in the factory menu based on
    ``factories_order``.
    """
    portal_type = context.portal_type
    pt = getToolByName(context, 'portal_types')
    fti = pt[portal_type]

    factories_order = ['Task',
                       'Add Participant',
                       'Document',
                       'document_with_template',
                       'Document with docucomposer',
                       fti.title,
                       'Add task from template']

    ordered_factories = []
    for factory_title in factories_order:
        try:
            factory = [f for f in factories if f.get(
                'title') == factory_title][0]
            ordered_factories.append(factory)
        except IndexError:
            pass

    remaining_factories = [
        f for f in factories if f.get('title') not in factories_order]

    all_factories = ordered_factories + remaining_factories
    return all_factories
