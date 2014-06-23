from ftw.upgrade import UpgradeStep


class AddReviewerOnAdmin(UpgradeStep):

    def __call__(self):

        prm = self.portal.acl_users.portal_role_manager

        for group in prm.listAssignedPrincipals('Administrator'):
            prm.assignRoleToPrincipal('Reviewer', group[0])
