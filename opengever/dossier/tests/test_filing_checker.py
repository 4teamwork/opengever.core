from ftw.testing import MockTestCase
from ftw.testing.layer import ComponentRegistryLayer
from opengever.base.interfaces import IBaseClientID
from opengever.dossier.archive import FILING_NO_KEY
from opengever.dossier.behaviors.dossier import IDossier, IDossierMarker
from opengever.dossier.filing_checker import FilingNumberChecker
from opengever.dossier.filing_checker import Checker
from plone.registry.interfaces import IRegistry
from zope.annotation import IAnnotations
from zope.interface import Interface


TEST_CLIENT_ID = 'SKA ARCH'


class ZCMLLayer(ComponentRegistryLayer):

    def setUp(self):
        super(ZCMLLayer, self).setUp()

        import zope.annotation
        self.load_zcml_file('configure.zcml', zope.annotation)

ZCML_LAYER = ZCMLLayer()


class MockChecker(Checker):
    def check_something(self):
        """Check for something.
        """
        return 'something'

    def check_something_else(self):
        """Some other docstring.
        """
        return 'something else'

    def dummy(self):
        pass


class TestChecker(MockTestCase):

    layer = ZCML_LAYER

    def setUp(self):
        self.plone = self.stub()

    def tearDown(self):
        del self.plone

    def mock_options(self, value=False):
        options = self.mocker.mock()
        self.expect(options.verbose).result(value)
        return options

    def test_run(self):
        checker = MockChecker(self.stub())
        self.replay()
        # Test that all methods starting with 'checker_' have been gathered...
        self.assertIn(checker.check_something, checker.checkers)
        self.assertIn(checker.check_something_else, checker.checkers)
        # ... but not any other ones
        self.assertNotIn(checker.dummy, checker.checkers)

        # Test that all the checkers are run and results stored properly
        checker.run()
        self.assertEquals(checker.results,
            {'check_something_else': 'something else',
             'check_something': 'something'})

    def test_checker_title(self):
        checker = MockChecker(self.stub())
        self.replay()
        check1 = checker.check_something
        check2 = checker.check_something_else
        self.assertEquals(checker.get_checker_title(check1),
                    "Something")
        self.assertEquals(checker.get_checker_title(check2),
                    "Some other docstring")

    def test_format_result_line(self):
        checker = MockChecker(self.stub())
        self.replay()
        items = ["a", "b", "c", "d"]
        result_line = checker.format_result_line(items)
        expected = 'a' + ' ' * 35 + 'b' + ' ' * 25 + 'c d\n'
        self.assertEquals(result_line, expected)

    def test_format_results(self):
        checker = MockChecker(self.mock_options())
        self.replay()
        checker.results = {'check_something': ['aaa', 'AAA'],
                           'check_something_else': ['bbb', 'BBB']}
        # Just test the format_results() method doesn't fail, don't
        # make assertions about its result
        checker.format_results()

    def test_format_results_verbose(self):
        checker = MockChecker(self.mock_options(True))
        self.replay()
        checker.results = {'check_something': ['aaa', 'AAA'],
                           'check_something_else': ['bbb', 'BBB']}
        # Just test the format_results() method doesn't fail, don't
        # make assertions about its result
        checker.format_results()


class TestFilingNumberChecker(MockTestCase):

    layer = ZCML_LAYER

    def setUp(self):
        self.plone = self.stub()
        self.options = self.mock_options()

    def tearDown(self):
        del self.plone
        del self.options

    def mock_base_client_id_registry(self, client_id=TEST_CLIENT_ID):
        registry = self.stub()
        self.mock_utility(registry, IRegistry)
        proxy = self.stub()
        self.expect(registry.forInterface(IBaseClientID)).result(proxy)
        self.expect(proxy.client_id).result(client_id)

    def mock_counter_annotations(self, portal, counters, count=1):
        annotation_factory = self.mocker.mock()
        self.mock_adapter(annotation_factory, IAnnotations, (Interface,))
        self.expect(annotation_factory(portal)
                   ).result({FILING_NO_KEY: counters}).count(count)

    def mock_dossier_brains(self, data):
        mock_dossier_brains = []
        for filing_no, path in data:
            stub_dossier = self.providing_stub([IDossier, IDossierMarker])
            self.expect(stub_dossier.filing_no).result(filing_no)

            mock_brain = self.mocker.mock()
            self.expect(mock_brain.getObject()).result(stub_dossier).count(2)
            self.expect(mock_brain.getPath()).result(path).count(1)
            mock_dossier_brains.append(mock_brain)
        return mock_dossier_brains

    def mock_options(self):
        options = self.mocker.mock()
        self.expect(options.site_root).result('ska-arch')
        return options

    def mock_catalog(self, dossier_data):
        catalog = self.stub()
        self.mock_tool(catalog, 'portal_catalog')

        mock_dossier_brains = self.mock_dossier_brains(dossier_data)
        DOSSIER_MARKER = 'opengever.dossier.behaviors.dossier.IDossierMarker'
        self.expect(catalog(object_provides=DOSSIER_MARKER)
                   ).result(mock_dossier_brains)

    def mock_counter(self, value):
        mock_counter = self.mocker.mock()
        self.expect(mock_counter.value).result(value)
        return mock_counter

    def test_duplicates(self):
        dossier_data = [('SKA ARCH-Amt-2012-1', '/dossier1'),  # duplicate
                        ('SKA ARCH-Amt-2012-1', '/dossier2'),  # duplicate
                        ('SKA ARCH-Amt-2012-7', '/dossier3')]  # OK
        self.mock_catalog(dossier_data)
        self.mock_base_client_id_registry()

        self.replay()
        checker = FilingNumberChecker(self.options, self.plone)
        results = checker.check_for_duplicates()
        self.assertEquals(results, [
                ('SKA ARCH-Amt-2012-1', '/dossier1'),
                ('SKA ARCH-Amt-2012-1', '/dossier2')])

    def test_fuzzy_duplicates(self):
        dossier_data = [('SKA ARCH-Amt-2012-1', '/dossier1'),  # duplicate
                        ('SKA.ARCH-Amt-2012-1', '/dossier2'),  # duplicate
                        ('SKA ARCH-Amt-2012-2', '/dossier3'),  # duplicate
                        ('SKA ARCH-Amt-2012-2', '/dossier4'),  # duplicate
                        ('SKA ARCH-Amt-2012-7', '/dossier5')]  # OK
        self.mock_catalog(dossier_data)
        self.mock_base_client_id_registry()

        self.replay()
        checker = FilingNumberChecker(self.options, self.plone)
        results = checker.check_for_fuzzy_duplicates()
        self.assertEquals(results, [
                ('Amt-2012-1', 'SKA ARCH-Amt-2012-1', '/dossier1'),
                ('Amt-2012-1', 'SKA.ARCH-Amt-2012-1', '/dossier2'),
                ('Amt-2012-2', 'SKA ARCH-Amt-2012-2', '/dossier3'),
                ('Amt-2012-2', 'SKA ARCH-Amt-2012-2', '/dossier4')])

    def test_legacy_filing_prefixes(self):
        dossier_data = [('Finanzdirektion-2012-1',  '/dossier1'),  # legacy
                        ('FD FDS-Direktion-2012-2', '/dossier2')]  # OK
        self.mock_catalog(dossier_data)
        self.mock_base_client_id_registry()

        self.replay()
        checker = FilingNumberChecker(self.options, self.plone)
        checker.legacy_prefixes = {u'Finanzdirektion': u'Direktion'}
        results = checker.check_for_legacy_filing_prefixes()
        self.assertEquals(results, [('Finanzdirektion-2012-1', '/dossier1')])

    def test_missing_client_prefixes(self):
        dossier_data = [('Amt-2012-1',          '/dossier1'),  # missing prefix
                        ('SKA ARCH-Amt-2012-2', '/dossier2'),  # OK
                        ('FD FDS-Amt-2012-3',   '/dossier3')]  # wrong client
        self.mock_catalog(dossier_data)
        self.mock_base_client_id_registry('SKA ARCH')

        self.replay()
        checker = FilingNumberChecker(self.options, self.plone)
        results = checker.check_for_missing_client_prefixes()
        self.assertEquals(results, [('Amt-2012-1',        '/dossier1'),
                                    ('FD FDS-Amt-2012-3', '/dossier3')])

    def test_dotted_client_prefixes(self):
        dossier_data = [('FD FDS-Amt-2012-1', '/dossier1'),  # OK
                        ('FD.FDS-Amt-2012-2', '/dossier2'),  # dotted prefix
                        ]
        self.mock_catalog(dossier_data)
        self.mock_base_client_id_registry(client_id='FD FDS')

        self.replay()
        checker = FilingNumberChecker(self.options, self.plone)
        results = checker.check_for_dotted_client_prefixes()
        self.assertEquals(results, [('FD.FDS-Amt-2012-2', '/dossier2')])

    def test_bad_counters(self):
        counters = {'Amt-2012': self.mock_counter(77),
                    'Xyz-2012': self.mock_counter(99)}
        dossier_data = [('FD FDS-Amt-2012-1',  '/dossier1'),  # OK
                        ('FD FDS-Amt-2012-78', '/dossier2'),  # too high
                        ('FD FDS-Xyz-2012-99', '/dossier3')]  # OK
        self.mock_catalog(dossier_data)
        self.mock_counter_annotations(self.plone, counters)
        self.mock_base_client_id_registry(client_id='FD FDS')

        self.replay()
        checker = FilingNumberChecker(self.options, self.plone)
        results = checker.check_for_bad_counters()
        self.assertEquals(results[0][0], 'Amt-2012')
        self.assertEquals(results[0][2], 'FD FDS-Amt-2012-78')
