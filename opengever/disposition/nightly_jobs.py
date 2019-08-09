from opengever.disposition.delivery import DeliveryScheduler
from opengever.disposition.interfaces import IDisposition
from opengever.nightlyjobs.interfaces import INightlyJobProvider
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
import logging


@implementer(INightlyJobProvider)
@adapter(IPloneSiteRoot, IBrowserRequest, logging.Logger)
class NightlySIPDelivery(object):
    """Nightly job provider that delivers SIP packages scheduled for delivery.
    """

    def __init__(self, context, request, logger):
        self.context = context
        self.request = request
        self.logger = logger

        self.catalog = api.portal.get_tool('portal_catalog')

    def _get_dispositions_for_delivery(self):
        """Get all dispositions that are in status 'disposed' and have a SIP.
        """
        query = dict(
            object_provides=IDisposition.__identifier__,
            review_state='disposition-state-disposed',
        )
        brains = self.catalog.unrestrictedSearchResults(query)
        for brain in brains:
            disposition = brain.getObject()
            if disposition.is_scheduled_for_delivery():
                yield disposition

    def __iter__(self):
        return iter(list(self._get_dispositions_for_delivery()))

    def __len__(self):
        return len(list(self._get_dispositions_for_delivery()))

    def run_job(self, job, interrupt_if_necessary):
        disposition = job
        self.logger.info("Delivering SIP for %r" % disposition)
        DeliveryScheduler(disposition, parent_logger=self.logger).deliver()
