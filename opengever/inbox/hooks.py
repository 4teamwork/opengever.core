from plone import api


ACTIONS_ORDER = ['overview',
                 'documents',
                 'assigned_inbox_tasks',
                 'issued_inbox_tasks',
                 'trash',
                 'journal',
                 'sharing']


def order_actions(context):
    """ Order the actions on the opengever.inbox.inbox FTI according to the
    order given in ACTIONS_ORDER.

    """
    pt = api.portal.get_tool('portal_types')
    inbox_fti = pt['opengever.inbox.inbox']

    actions = inbox_fti._actions

    ordered_actions = []
    for action_id in ACTIONS_ORDER:
        action = [a for a in actions if a.id == action_id][0]
        ordered_actions.append(action)

    remaining_actions = [a for a in actions if a.id not in ACTIONS_ORDER]

    all_actions = ordered_actions + remaining_actions
    inbox_fti._actions = all_actions


def installed(site):
    order_actions(site)
