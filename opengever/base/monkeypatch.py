from ZODB.POSException import ConflictError
import logging


LOGGER = logging.getLogger('opengever.base')


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
