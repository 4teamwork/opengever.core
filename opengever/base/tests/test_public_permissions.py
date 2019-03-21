from AccessControl.Permission import getPermissions
from opengever.base.public_permissions import PUBLIC_PERMISSIONS_MAPPING
from opengever.testing import FunctionalTestCase


class TestPublicPermissionMapping(FunctionalTestCase):

    def test_all_public_permissions_are_mapped_to_real_permissions(self):
        existing_permissions = map(lambda permission: permission[0], getPermissions())

        for public_name, permission in PUBLIC_PERMISSIONS_MAPPING.items():
            self.assertIn(
                permission, existing_permissions,
                "{} is mapped to an unnokwn permission {}".format(public_name, permission))
