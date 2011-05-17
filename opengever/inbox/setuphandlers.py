"""Contains setuphandlers"""
from Products.CMFCore.utils import getToolByName


# The profile id of your package:
PROFILE_ID = 'profile-opengever.inbox:default'


ACTIONS_ORDER = ['overview',
                 'documents',
                 'assigned_forwardings',
                 'given_tasks',
                 'assigned_tasks',
                 'trash',
                 'journal',
                 'sharing']


def order_actions(context):
    """ Order the actions on the opengever.inbox.inbox FTI
    according to the order given in ACTIONS_ORDER
    """

    pt = getToolByName(context, 'portal_types')
    inbox_fti = pt['opengever.inbox.inbox']

    actions = inbox_fti._actions

    ordered_actions = []
    for action_id in ACTIONS_ORDER:
        action = [a for a in actions if a.id == action_id][0]
        ordered_actions.append(action)

    remaining_actions = [a for a in actions if a.id not in ACTIONS_ORDER]

    all_actions = ordered_actions + remaining_actions
    inbox_fti._actions = all_actions


def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    if context.readDataFile('opengever.inbox_various.txt') is None:
        return
    #logger = context.getLogger('opengever.inbox')
    site = context.getSite()
    order_actions(site)

