from plone import api
from ZODB.POSException import ConflictError
from zope.globalrequest import getRequest
from zope.i18nmessageid import MessageFactory
import logging
import traceback


logger = logging.getLogger('opengever.activity')
_ = MessageFactory("opengever.activity")


class NotificationErrorHandler(object):
    """Context manager to prevent notification dispatching from causing
    issues through unhandled exceptions during dispatch.
    """

    def __enter__(self):
        return self

    def __exit__(self, _type, exc, _traceback):
        if isinstance(exc, ConflictError):
            return False  # Propagate

        if exc is not None:
            self.show_not_notified_message()

            tb = ''.join(traceback.format_exception(_type, exc, _traceback))
            logger.error('Exception while adding an activity:\n{}'.format(tb))
            return True

    def show_not_notified_message(self):
        msg = _(u'msg_error_not_notified',
                default=u'A problem has occurred during the notification '
                'creation. Notification could not or only partially '
                'produced.')
        api.portal.show_message(msg, getRequest(), type='warning')
