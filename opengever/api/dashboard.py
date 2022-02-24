from opengever.base.interfaces import IGeverUI
from plone import api
from plone.restapi.services import Service
import json


class DashboardSettings(Service):

    def reply(self):
        return {'cards': json.loads(api.portal.get_registry_record(
            'custom_dashboard_cards', interface=IGeverUI))}
