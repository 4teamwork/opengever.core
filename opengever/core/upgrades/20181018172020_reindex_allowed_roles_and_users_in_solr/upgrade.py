from ftw.upgrade import UpgradeStep
from opengever.base.interfaces import ISearchSettings
from plone import api
from zope.component import queryMultiAdapter


class ReindexAllowedRolesAndUsersInSolr(UpgradeStep):
    """Reindex allowedRolesAndUsers in Solr after bumping ftw.solr to a
    version that also patches reindexObjectSecurity().
    """

    deferrable = True

    def __call__(self):
        solr_enabled = api.portal.get_registry_record(
            name='use_solr', interface=ISearchSettings)
        if not solr_enabled:
            return

        portal = api.portal.get()
        solr_maintenance = queryMultiAdapter(
            (portal, portal.REQUEST), name=u'solr-maintenance')

        solr_maintenance.reindex(
            idxs=['allowedRolesAndUsers'], doom=False)
