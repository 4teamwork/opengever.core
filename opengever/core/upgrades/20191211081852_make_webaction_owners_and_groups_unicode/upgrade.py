from ftw.upgrade import UpgradeStep
from opengever.webactions.storage import get_storage
from Products.CMFPlone.utils import safe_unicode


class MakeWebactionOwnersAndGroupsUnicode(UpgradeStep):
    """Make webaction owners and groups unicode.
    """

    deferrable = True

    def __call__(self):
        storage = get_storage()
        for action in storage._actions.values():
            action['owner'] = safe_unicode(action['owner'])
            if 'groups' in action:
                action['groups'] = map(safe_unicode,
                                       action['groups'])
