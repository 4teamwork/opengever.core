from AccessControl.SecurityManagement import getSecurityManager
from opengever.base.error_log import ErrorLogItem
from opengever.base.error_log import get_error_log
from opengever.base.monkey.patching import MonkeyPatch
from Products.SiteErrorLog.SiteErrorLog import cleanup_lock
from Products.SiteErrorLog.SiteErrorLog import LOG
from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
from random import random
from zExceptions.ExceptionFormatter import format_exception
import sys
import time


class PatchSiteErrorLog(MonkeyPatch):
    """
    """

    def __call__(self):
        def raising(self, info):
            """Log an exception.

            Called by SimpleItem's exception handler.
            Returns the url to view the error log entry
            """
            try:
                now = time.time()
                try:
                    tb_text = None
                    tb_html = None

                    strtype = str(getattr(info[0], '__name__', info[0]))
                    if strtype in self._ignored_exceptions:
                        return

                    if not isinstance(info[2], basestring):
                        tb_text = ''.join(
                            format_exception(*info, **{'as_html': 0}))
                        tb_html = ''.join(
                            format_exception(*info, **{'as_html': 1}))
                    else:
                        tb_text = info[2]

                    request = getattr(self, 'REQUEST', None)
                    url = None
                    username = None
                    userid   = None
                    req_html = None
                    try:
                        strv = str(info[1])
                    except:
                        strv = '<unprintable %s object>' % type(info[1]).__name__
                    if request:
                        url = request.get('URL', '?')
                        usr = getSecurityManager().getUser()
                        username = usr.getUserName()
                        userid = usr.getId()
                        try:
                            req_html = str(request)
                        except:
                            pass
                        if strtype == 'NotFound':
                            strv = url
                            next = request['TraversalRequestNameStack']
                            if next:
                                next = list(next)
                                next.reverse()
                                strv = '%s [ /%s ]' % (strv, '/'.join(next))

                    log = self._getLog()
                    entry_id = str(now) + str(random()) # Low chance of collision
                    log.append({
                        'type': strtype,
                        'value': strv,
                        'time': now,
                        'id': entry_id,
                        'tb_text': tb_text,
                        'tb_html': tb_html,
                        'username': username,
                        'userid': userid,
                        'url': url,
                        'req_html': req_html,
                        })
                    # CUSTOM - Log entry to redis
                    try:
                        log_item = log[-1]
                        get_error_log().push(ErrorLogItem(error=log_item.get('value'), **log_item))
                    except Exception:
                        LOG.error('Error while logging to redis', exc_info=sys.exc_info())
                    # END CUSTOM
                    cleanup_lock.acquire()
                    try:
                        if len(log) >= self.keep_entries:
                            del log[:-self.keep_entries]
                    finally:
                        cleanup_lock.release()
                except:
                    LOG.error('Error while logging', exc_info=sys.exc_info())
                else:
                    if self.copy_to_zlog:
                        self._do_copy_to_zlog(now,strtype,entry_id,str(url),tb_text)
                    return '%s/showEntry?id=%s' % (self.absolute_url(), entry_id)
            finally:
                info = None

        self.patch_refs(SiteErrorLog, "raising", raising)
