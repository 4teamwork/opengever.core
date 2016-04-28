from ZODB.POSException import ConflictError
import logging


LOGGER = logging.getLogger('opengever.base')


# Monkey patch the regex used to replace relative paths in url() statements
# with absolute paths in the portal_css tool.
# This has been fixed as of release 3.0.3 of Products.ResourceRegistries
# which is only available for Plone 5.
# See https://github.com/plone/Products.ResourceRegistries/commit/4f9094919bc1c50404e74c748b067a3563e640aa

import re
from Products.ResourceRegistries import utils


utils.URL_MATCH = re.compile(r'''(url\s*\(\s*['"]?)(?!data:)([^'")]+)(['"]?\s*\))''', re.I | re.S)


LOGGER.info('Monkey patched Products.ResourceRegistries.utils.URL_MATCH regexp')


# --------
# Patch for Products.CMFEditions.historyidhandlertool
#           .HistoryIdHandlerTool.register
#
# The default "register" method uses the Products.CMFUid IUniqueIdGenerator
# utility for generating the history ID. This utility uses the auto-increment
# strategy, which generates a lot of conflicts.
#
# In order to reduce the conflicts when generating the history id,
# we switch to the uuid4 implementation, generating a random number instead
# and thus not writing to the same place.

from Products.CMFEditions.historyidhandlertool import HistoryIdHandlerTool
from uuid import uuid4


def HistoryIdHandlerTool_register(self, obj):
    uid = self.queryUid(obj, default=None)
    if uid is None:
        # generate a new unique id and set it
        uid = uuid4().int
        self._setUid(obj, uid)

    return uid


HistoryIdHandlerTool.register = HistoryIdHandlerTool_register
LOGGER.info('Monkey patched Products.CMFEditions.historyidhandlertool'
            '.HistoryIdHandlerTool.register')
