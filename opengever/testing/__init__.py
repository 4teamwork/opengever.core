import pkg_resources

try:
    pkg_resources.get_distribution('ftw.testing')

except pkg_resources.DistributionNotFound:
    # [tests] is not installed - z3c.autoinclude is scanning.
    pass
else:
    from opengever.core.testing import MEMORY_DB_LAYER
    from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
    from opengever.testing.helpers import add_languages
    from opengever.testing.helpers import create_plone_user
    from opengever.testing.helpers import index_data_for
    from opengever.testing.helpers import localized_datetime
    from opengever.testing.helpers import obj2brain
    from opengever.testing.helpers import obj2paths
    from opengever.testing.helpers import set_preferred_language
    from opengever.testing.sql import assign_user_to_client
    from opengever.testing.sql import create_ogds_user
    from opengever.testing.sql import select_current_org_unit
    from opengever.testing.test_case import FunctionalTestCase
    from opengever.testing.integration_test_case import IntegrationTestCase
    from opengever.testing.integration_test_case import SolrIntegrationTestCase
    from opengever.testing.test_case import TestCase
    import opengever.testing.testbrowser_datetime_widget
    import opengever.testing.testbrowser_tablechoice_widget
    import opengever.testing.testbrowser_responsible_user_widget
