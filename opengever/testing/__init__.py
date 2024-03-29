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
    from opengever.testing.helpers import obj2solr
    from opengever.testing.helpers import set_preferred_language
    from opengever.testing.helpers import solr_data_for
    from opengever.testing.integration_test_case import IntegrationTestCase
    from opengever.testing.integration_test_case import SolrIntegrationTestCase
    from opengever.testing.sql import assign_user_to_client
    from opengever.testing.sql import create_ogds_user
    from opengever.testing.sql import select_current_org_unit
    from opengever.testing.test_case import FunctionalTestCase
    from opengever.testing.test_case import SolrFunctionalTestCase
    from opengever.testing.test_case import TestCase
    import opengever.testing.testbrowser_datetime_widget  # noqa
    import opengever.testing.testbrowser_responsible_user_widget  # noqa
    import opengever.testing.testbrowser_tablechoice_widget  # noqa

    __all__ = [
        'MEMORY_DB_LAYER',
        'OPENGEVER_FUNCTIONAL_TESTING',
        'add_languages',
        'create_plone_user',
        'index_data_for',
        'localized_datetime',
        'obj2brain',
        'obj2paths',
        'obj2solr',
        'set_preferred_language',
        'solr_data_for',
        'IntegrationTestCase',
        'SolrIntegrationTestCase',
        'assign_user_to_client',
        'create_ogds_user',
        'select_current_org_unit',
        'FunctionalTestCase',
        'SolrFunctionalTestCase',
        'TestCase',
    ]
