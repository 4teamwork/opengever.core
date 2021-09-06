from opengever.nightlyjobs.interfaces import INightlyJobProvider
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
import logging
import transaction


@implementer(INightlyJobProvider)
@adapter(IPloneSiteRoot, IBrowserRequest, logging.Logger)
class NightlyJobProviderBase(object):

    def __init__(self, context, request, logger):
        self.context = context
        self.request = request
        self.logger = logger

    def maybe_commit(self, job):
        transaction.commit()
