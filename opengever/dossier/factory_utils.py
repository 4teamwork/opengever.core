"""
This module contains utility function used by the differents specialdossiers
behaviors' PostFactoryMenu adapters.

"""


def order_factories(context, factories):
    """Orders the entries in the factory menu based on
    ``factories_order``.
    """

    factories_order = ['Document',
                       'Document with docucomposer',
                       'Document with docugate',
                       'document_with_template',
                       'Task',
                       'Add task from template',
                       'Mail',
                       'Subdossier',
                       'Add Participant',
                    ]

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
