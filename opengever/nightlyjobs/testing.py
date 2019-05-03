from opengever.nightlyjobs.interfaces import INightlyJobProvider
from opengever.nightlyjobs.runner import NightlyJobRunner
from plone import api
from zope.component import getAdapters
from zope.globalrequest import getRequest


class ITestingNightlyJobProvider(INightlyJobProvider):
    """Interface to mark a job provider used for testing only.
    """


class TestingNightlyJobRunner(NightlyJobRunner):
    """Nightly job runner used for testing.

    This runner *only* collects nightly job providers providing
    ITestingNightlyJobProvider, and therefore ignores real job providers
    that would otherwise interfere with testing conditions.
    """

    def get_job_providers(self):
        return {name: provider for name, provider
                in getAdapters([api.portal.get(), getRequest(), self.log],
                               ITestingNightlyJobProvider)}
