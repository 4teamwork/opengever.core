from opengever.disposition.delivery import DeliveryScheduler
from opengever.disposition.interfaces import IDisposition
from opengever.nightlyjobs.provider import NightlyJobProviderBase
from plone import api


class NightlySIPDelivery(NightlyJobProviderBase):
    """Nightly job provider that delivers SIP packages scheduled for delivery.
    """

    def __init__(self, context, request, logger):
        super(NightlySIPDelivery, self).__init__(context, request, logger)

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
