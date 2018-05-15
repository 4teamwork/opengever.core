from ftw.upgrade import UpgradeStep
from opengever.base.interfaces import ISearchSettings
from plone import api
from zope.component import queryMultiAdapter


class ReindexSubjectIndexOnSolr(UpgradeStep):
    """Reindex Subject index on solr.

    ! Potentially long running and not absolutely necessary,
    could also be done via an maintenance job/script.
    """

    def __call__(self):
        solr_enabled = api.portal.get_registry_record(
            name='use_solr', interface=ISearchSettings)
        if not solr_enabled:
            return

        portal = api.portal.get()
        solr_maintenance = queryMultiAdapter(
            (portal, portal.REQUEST), name=u'solr-maintenance')

        solr_maintenance.reindex(idxs=['Subject'], doom=False)
