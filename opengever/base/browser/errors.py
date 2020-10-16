from Acquisition import aq_acquire
from opengever.debug import write_on_read_tracing
from opengever.debug.write_on_read_tracing import format_instruction
from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import NotFound
from ZODB import POSException
from zope.component import adapts
from zope.component.hooks import getSite
from zope.interface import Interface
import sys
import traceback


class ErrorHandlingView(BrowserView):
    adapts(Exception, Interface)
    template = ViewPageTemplateFile('templates/error.pt')

    def __call__(self):
        self.plone = getSite()

        if self.plone:
            self.portal_state = self.plone.unrestrictedTraverse(
                '@@plone_portal_state')
            self.portal_url = self.portal_state.portal_url()
            self.language = self.portal_state.language()
        else:
            self.portal_state = None
            self.portal_url = ''
            self.language = 'de'

        self.request.response.setHeader('Content-Type', 'text/html')
        return self.template()

    def is_manager(self):
        if self.plone:
            return api.user.has_permission('cmf.ManagePortal')

    def is_notfound_error(self):
        return isinstance(self.context, NotFound)

    def is_readonly_error(self):
        return isinstance(self.context, POSException.ReadOnlyError)

    def get_culprit_traceback(self):
        instruction = write_on_read_tracing.tb_for_last_db_write
        if instruction is not None:
            return format_instruction(instruction)

    def get_error_log(self):
        log = None
        published = self.__parent__
        if published:
            try:
                error_log = aq_acquire(published,
                                       '__error_log__',
                                       containment=1)

                error_type, error_value, tb = sys.exc_info()
                error_log_url = error_log.raising((error_type,
                                                   error_value,
                                                   tb))
                log = {'url': error_log_url,
                       'errorid': error_log_url.split('?id=')[1],
                       'traceback': ''.join(traceback.format_exception(
                                            error_type,
                                            error_value,
                                            tb))
                       }
            except AttributeError:
                log = None

        return log
