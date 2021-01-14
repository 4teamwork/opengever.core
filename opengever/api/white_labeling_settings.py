from opengever.base.interfaces import IWhiteLabelingSettings
from plone import api
from plone.restapi.services import Service
import base64
import json


class WhiteLabelingSettingsGet(Service):

    def check_permission(self):
        return

    def reply(self):
        logo_src = api.portal.get_registry_record('logo_src', interface=IWhiteLabelingSettings)
        color_scheme_light = api.portal.get_registry_record(
            'color_scheme_light', interface=IWhiteLabelingSettings)

        result = {
            '@id': '{}/@white-labeling-settings'.format(self.context.absolute_url()),
            'custom_support_markup': {
                'de': api.portal.get_registry_record('custom_support_markup_de',
                                                     interface=IWhiteLabelingSettings),
                'en': api.portal.get_registry_record('custom_support_markup_en',
                                                     interface=IWhiteLabelingSettings),
                'fr': api.portal.get_registry_record('custom_support_markup_fr',
                                                     interface=IWhiteLabelingSettings),
            },
            'logo': {
                'src': 'data:image/png;base64,' + base64.b64encode(logo_src) if logo_src else None
            },
            'show_created_by': api.portal.get_registry_record('show_created_by',
                                                              interface=IWhiteLabelingSettings),
            'themes': {
                'light': json.loads(color_scheme_light) if color_scheme_light else {}
            }
        }
        return result
