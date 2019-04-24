from opengever.nightlyjobs.interfaces import INightlyJobProvider
from opengever.nightlyjobs.job_providers import NightlyJob
from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.uuid.utils import uuidToObject
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.component import getAdapters
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class ModifyTitleJob(NightlyJob):

    def __init__(self, provider_name, uid):
        self.uid = uid
        self.provider_name = provider_name


class IWantToBeModified(Interface):
    pass


class TestException(Exception):
    pass


@implementer(INightlyJobProvider)
@adapter(IPloneSiteRoot, IBrowserRequest)
class DocumentTitleModifierJobProvider(object):

    portal_type = 'opengever.document.document'
    provider_name = 'document-title'

    def __init__(self, context, request):
        self.context = context
        self.request = request

        catalog = api.portal.get_tool('portal_catalog')
        documents = catalog(portal_type=self.portal_type,
                            object_provides=IWantToBeModified.__identifier__,
                            sort_on='path')
        self._jobs = (NightlyJob(self.provider_name, {'uid': document.UID})
                      for document in documents)
        self._njobs = documents.actual_result_count
        self._njobs_executed = 0

    def __iter__(self):
        return self

    def next(self):
        return next(self._jobs)

    def __len__(self):
        return self._njobs - self._njobs_executed

    def run_job(self, job, interrupt_if_necessary):
        self.execute_job(job, interrupt_if_necessary)
        self._njobs_executed += 1

    def execute_job(self, job, interrupt_if_necessary):
        interrupt_if_necessary()
        obj = uuidToObject(job.uid)
        obj.title = u'Modified {}'.format(obj.title)


class TestNightlyJobProviderClasses(IntegrationTestCase):

    def test_all_providers_implement_interface(self):
        """ We test that all (actually just the most specific one for each
        provider name) implemented providers implement the INightlyJobProvider
        interface and the necessary methods.
        """
        # retrieve all providers
        job_providers = {name: provider for name, provider
                         in getAdapters([api.portal.get(), getRequest()],
                                        INightlyJobProvider)}
        for provider in job_providers.values():
            verifyObject(INightlyJobProvider, provider)
            verifyClass(INightlyJobProvider, provider.__class__)


class TestNightlyJobProvider(IntegrationTestCase):

    def setUp(self):
        super(TestNightlyJobProvider, self).setUp()
        self.portal = self.layer['portal']

        self.portal.getSiteManager().registerAdapter(DocumentTitleModifierJobProvider,
                                                     name='document-title')

        with self.login(self.regular_user):
            alsoProvides(self.document, IWantToBeModified)
            alsoProvides(self.subdocument, IWantToBeModified)
            alsoProvides(self.subsubdocument, IWantToBeModified)
            self.document.reindexObject(idxs=["object_provides"])
            self.subdocument.reindexObject(idxs=["object_provides"])
            self.subsubdocument.reindexObject(idxs=["object_provides"])

    def interrupt(self):
        raise TestException()

    def do_not_interrupt(self):
        return

    def test_job_provider_job_execution(self):
        self.login(self.manager)
        provider = getMultiAdapter([api.portal.get(), getRequest()],
                                   INightlyJobProvider,
                                   name='document-title')

        document_title = self.document.title
        provider.run_job(next(provider), self.do_not_interrupt)
        self.assertEqual(u'Modified {}'.format(document_title), self.document.title)

    def test_job_provider_job_counters(self):
        self.login(self.manager)
        provider = getMultiAdapter([api.portal.get(), getRequest()],
                                   INightlyJobProvider,
                                   name='document-title')
        self.assertEqual(3, len(provider))
        self.assertEqual(0, provider._njobs_executed)

        for i, job in enumerate(provider):
            provider.run_job(job, self.do_not_interrupt)
            self.assertEqual(3 - (i + 1), len(provider))
            self.assertEqual(i + 1, provider._njobs_executed)

    def test_job_provider_job_execution_interruption(self):
        self.login(self.manager)
        provider = getMultiAdapter([api.portal.get(), getRequest()],
                                   INightlyJobProvider,
                                   name='document-title')

        document_title = self.document.title
        with self.assertRaises(TestException):
            provider.run_job(next(provider), self.interrupt)

        self.assertEqual(document_title, self.document.title)
        self.assertEqual(0, provider._njobs_executed)
