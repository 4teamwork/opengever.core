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


def order_actions(site, logger):
    """ Order the actions on the opengever.inbox.inbox FTI
    according to the order given in ACTIONS_ORDER
    """

    pt = getToolByName(site, 'portal_types')
    inbox_fti = pt['opengever.inbox.inbox']

    # Get all actions, and append the ones
    # not yet listed in ACTIONS_ORDER to the end
    # (since we don't care about their order)
    actions = inbox_fti._actions
    all_actions = [a.id for a in actions]
    other_actions = set(all_actions) - set(ACTIONS_ORDER)
    ACTIONS_ORDER.extend(other_actions)

    for action_id in ACTIONS_ORDER:
        pos = 0
        target_pos = ACTIONS_ORDER.index(action_id)

        if actions and actions[target_pos].id != action_id:
            # Determine the action's current position
            for i in range(len(actions)):
                if actions[i].id == action_id:
                    pos = i
                    break

            if pos > target_pos:
            # If action is positioned too low, move it up,
            # otherwise move it down
                for i in range(pos, target_pos, -1):
                    inbox_fti.moveUpActions(selections=[i])
            else:
                for i in range(pos, target_pos):
                    inbox_fti.moveDownActions(selections=[i])
            logger.info("Moved '%s' action to position %s" % (action_id, target_pos))



def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    if context.readDataFile('opengever.inbox_various.txt') is None:
        return
    logger = context.getLogger('opengever.inbox')
    site = context.getSite()
    order_actions(site, logger)
