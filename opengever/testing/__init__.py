import pkg_resources

try:
    pkg_resources.get_distribution('ftw.testing')

except pkg_resources.DistributionNotFound:
    # [tests] is not installed - z3c.autoinclude is scanning.
    pass
else:
    from opengever.core.testing import MEMORY_DB_LAYER
    from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
    from opengever.core.testing import OPENGEVER_INTEGRATION_TESTING
    from opengever.testing.helpers import create_plone_user
    from opengever.testing.helpers import index_data_for
    from opengever.testing.helpers import obj2brain
    from opengever.testing.sql import assign_user_to_client
    from opengever.testing.sql import create_and_select_current_org_unit
    from opengever.testing.sql import create_client
    from opengever.testing.sql import create_ogds_user
    from opengever.testing.sql import select_current_org_unit
    from opengever.testing.sql import set_current_client_id
    from opengever.testing.test_case import FunctionalTestCase
