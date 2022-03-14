from opengever.base.interfaces import IGeverUI
from opengever.base.utils import get_preferred_language_code
from plone import api
from plone.dexterity.utils import safe_utf8
from plone.restapi.services import Service
import json


class DashboardSettings(Service):

    def reply(self):
        language_code = get_preferred_language_code()
        cards = json.loads(api.portal.get_registry_record(
            'custom_dashboard_cards', interface=IGeverUI))

        return {'cards': self.localized_dashboard_card(cards, language_code)}

    def localized_dashboard_card(self, cards, language_code):
        for card in cards:
            title = card.get('title_{}'.format(language_code)) or card.get('title', '')
            if title:
                card['title'] = safe_utf8(title)

        return cards
