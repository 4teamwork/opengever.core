from ftw.upgrade import UpgradeStep
from opengever.base.interfaces import ISearchSettings
from plone import api
from zope.component import queryMultiAdapter


class ReindexCheckedOutAndAllowedRolesAndUsersOnSolr(UpgradeStep):
    """Reindex checked_out and allowedRolesAndUsers on solr.
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

        # solr_maintenance.reindex(
        #     idxs=['checked_out', 'allowedRolesAndUsers'], doom=False)

        # Changed to only reindex checked_out, because the later upgrade step
        # 20181018172020_reindex_allowed_roles_and_users_in_solr will
        # reindex allowedRolesAndUser into Solr again in 2018.5.
        #
        # So for deployments where we skip 2018.4 and directly deploy 2018.5
        # or newer, we don't reindex allowedRolesAndUsers twice.
        solr_maintenance.reindex(
            idxs=['checked_out'], doom=False)
