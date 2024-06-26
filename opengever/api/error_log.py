from opengever.base import utils
from opengever.base.error_log import get_error_log_redis
from plone import api
from plone.restapi.services import Service


class ErrorLogGet(Service):
    def reply(self):
        items = self.get_log_items()
        return {
            '@id': '/'.join((self.context.absolute_url(), '@error-log')),
            "items": items,
            "items_total": len(items),
            "restricted_by_current_user": self.restrict_by_current_user()
        }

    def restrict_by_current_user(self):
        return not utils.is_administrator()

    def get_log_items(self):
        items = []
        error_log = get_error_log_redis()
        if self.restrict_by_current_user():
            items = error_log.list_all_by_userid(api.user.get_current().getId())
        else:
            items = error_log.list_all()
        return [item.serialize() for item in items]
