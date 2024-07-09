from opengever.base.error_log import get_error_log
from plone.restapi.services import Service


class ErrorLogGet(Service):
    def reply(self):
        items = self.get_log_items()
        return {
            '@id': '/'.join((self.context.absolute_url(), '@error-log')),
            "items": items,
            "items_total": len(items),
        }

    def get_log_items(self):
        return [item.serialize() for item in get_error_log().list_all()]
