from opengever.base.adapters import ReferenceNumberPrefixAdpater
from plone.restapi.services import Service


class ReferenceNumbersGet(Service):
    """API endpoint to get a list of repository numbers used or locked on the
    current context.

    GET /repository_folder/@reference-numbers
    """

    def reply(self):
        return ReferenceNumberPrefixAdpater(self.context).get_number_mapping()
