from opengever.base.interfaces import IConfigCheck
from opengever.base.interfaces import IConfigCheckManager
from plone import api
from zope.component import getAdapters
from zope.interface import implementer


@implementer(IConfigCheckManager)
class ConfigCheckManager(object):
    """Main object to handle config checks.

    This object provides functions to run and manage config checks provided
    by named IConfigCheck adapters.
    """
    def check_all(self):
        errors = [config_check.check() for config_check in self._get_all_checks()]
        return filter(lambda value: value, errors)

    def _get_all_checks(self):
        for name, adapter in getAdapters((api.portal.get(), ), IConfigCheck):
            yield adapter
