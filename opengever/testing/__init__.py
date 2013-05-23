import pkg_resources

try:
    pkg_resources.get_distribution('ftw.testing')

except pkg_resources.DistributionNotFound:
    # [tests] is not installed - z3c.autoinclude is scanning.
    pass

else:
    from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
    from opengever.core.testing import OPENGEVER_INTEGRATION_TESTING
    from opengever.testing.builders import BuilderSession
    from opengever.testing.builders import ContactBuilder
    from opengever.testing.builders import DossierBuilder
    from opengever.testing.builders import DocumentBuilder
    from opengever.testing.builders import MailBuilder
    from opengever.testing.builders import TaskBuilder
    from opengever.testing.builders import RepositoryBuilder
    from opengever.testing.helpers import create_plone_user
    from opengever.testing.helpers import obj2brain
    from opengever.testing.helpers import index_data_for
    from opengever.testing.sql import create_client
    from opengever.testing.sql import create_ogds_user
    from opengever.testing.sql import assign_user_to_client
    from opengever.testing.sql import set_current_client_id
    from opengever.testing.test_case import FunctionalTestCase

    def Builder(name):
        if name == "dossier":
            return DossierBuilder(BuilderSession.instance())
        elif name == "document":
            return DocumentBuilder(BuilderSession.instance())
        elif name == "task":
            return TaskBuilder(BuilderSession.instance())
        elif name == "mail":
            return MailBuilder(BuilderSession.instance())
        elif name == "repository":
            return RepositoryBuilder(BuilderSession.instance())
        elif name == "contact":
            return ContactBuilder(BuilderSession.instance())
        else:
            raise ValueError("No Builder for %s" % name)
