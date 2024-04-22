from opengever.base.listing_actions import BaseListingActions
from opengever.base.utils import is_administrator


class UserListingActions(BaseListingActions):
    def is_export_users_available(self):
        return is_administrator()

    def is_delete_available(self):
        return False
