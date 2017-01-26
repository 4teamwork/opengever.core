from ftw.upgrade import UpgradeStep
from zope.annotation import IAnnotations


class ReplaceFooterWithStaticViewlets(UpgradeStep):
    """Replace footer with static viewlets.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.remove_footer_layer()
        self.remove_footer_portlets()
        self.remove_footer_portlet_managers()

    def remove_footer_layer(self):
        self.remove_broken_browserlayer('ftw.footer', 'IFtwFooterLayer')

    def remove_footer_portlets(self):
        assignments = (IAnnotations(self.portal)
                       .get('plone.portlets.contextassignments', {}))
        assignments.pop('ftw.footer.column1', None)
        assignments.pop('ftw.footer.column2', None)
        assignments.pop('ftw.footer.column3', None)
        assignments.pop('ftw.footer.column4', None)

    def remove_footer_portlet_managers(self):
        self.remove_broken_portlet_manager('ftw.footer.column1')
        self.remove_broken_portlet_manager('ftw.footer.column2')
        self.remove_broken_portlet_manager('ftw.footer.column3')
        self.remove_broken_portlet_manager('ftw.footer.column4')
