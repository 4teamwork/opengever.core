from ftw.testing import MockTestCase
from ftw.testing.layer import ComponentRegistryLayer
from opengever.base.interfaces import IBaseClientID
from opengever.dossier.archive import FILING_NO_KEY
from opengever.dossier.behaviors.dossier import IDossier, IDossierMarker
from opengever.dossier.filing_checker import FilingNumberChecker
from opengever.dossier.filing_checker import FilingNumberHelper
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


class FilingNumberMockTestCase(MockTestCase):
    """Base class that provides some helper methods to mock filing number
    related objects.
    """

    layer = ZCML_LAYER

    def setUp(self):
        self.options = self.stub_options()
        # Only register one dossier annotation factory adapter
        self.dossier_annotation_factory = self.mocker.mock()
        self.mock_adapter(self.dossier_annotation_factory, IDossier, (Interface,))

    def tearDown(self):
        del self.options
        del self.dossier_annotation_factory

    def mock_base_client_id_registry(self, client_id=TEST_CLIENT_ID):
        registry = self.stub()
        self.mock_utility(registry, IRegistry)
        proxy = self.stub()
        self.expect(registry.forInterface(IBaseClientID)).result(proxy)
        self.expect(proxy.client_id).result(client_id)

    def mock_counter(self, value, count=1):
        mock_counter = self.mocker.mock()
        self.expect(mock_counter.value).result(value).count(count)
        return mock_counter

    def mock_counter_annotations(self, portal, counters, count=1):
        annotation_factory = self.mocker.mock()
        self.mock_adapter(annotation_factory, IAnnotations, (Interface,))
        if counters is not None:
            self.expect(annotation_factory(portal)
                        ).result({FILING_NO_KEY: counters}).count(count)

    def mock_dossier(self):
        dossier_obj = self.providing_stub([IDossierMarker])
        dossier = self.mocker.mock()
        self.expect(self.dossier_annotation_factory(dossier_obj)).result(dossier)
        return (dossier_obj, dossier)

    def mock_dossier_brains(self, data):
        mock_dossier_brains = []
        for filing_no, path in data:
            dossier_obj, dossier = self.mock_dossier()
            mock_brain = self.mocker.mock()
            self.expect(dossier.filing_no).result(filing_no)
            self.expect(mock_brain.getObject()).result(dossier_obj)
            self.expect(mock_brain.getPath()).result(path)
            mock_dossier_brains.append(mock_brain)
        return mock_dossier_brains

    def stub_options(self, site_root='ska-arch'):
        options = self.stub()
        self.expect(options.site_root).result(site_root)
        return options

    def mock_options(self, **kwargs):
        options = self.mocker.mock()
        for key, value in kwargs.items():
            self.expect(getattr(options, key)).result(value)
        return options

    def mock_catalog(self, dossier_data):
        catalog = self.stub()
        self.mock_tool(catalog, 'portal_catalog')

        mock_dossier_brains = self.mock_dossier_brains(dossier_data)
        DOSSIER_MARKER = 'opengever.dossier.behaviors.dossier.IDossierMarker'
        self.expect(catalog(object_provides=DOSSIER_MARKER)
                   ).result(mock_dossier_brains)

    def mock_plone(self, site_id='ska-arch'):
        plone = self.mocker.mock()
        self.expect(plone.id).result(site_id)
        return plone


class TestChecker(FilingNumberMockTestCase):

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

    def test_format_result_line_numbers(self):
        checker = MockChecker(self.stub())
        self.replay()
        items = [1, 2, 3]
        result_line = checker.format_result_line(items)
        self.assertIn('1', result_line)
        self.assertIn('2', result_line)
        self.assertIn('3', result_line)

    def test_format_result_line_non_ascii(self):
        checker = MockChecker(self.stub())
        self.replay()
        items = [u'\xe4', u'\xf6', u'\xfc']
        result_line = checker.format_result_line(items)
        self.assertIn('\xc3\xa4', result_line)
        self.assertIn('\xc3\xb6', result_line)
        self.assertIn('\xc3\xbc', result_line)

    def test_format_results(self):
        checker = MockChecker(self.mock_options(verbose=False))
        self.replay()
        checker.results = {'check_something': ['aaa', 'AAA'],
                           'check_something_else': ['bbb', 'BBB']}
        # Just test the format_results() method doesn't fail, don't
        # make assertions about its result
        checker.format_results()

    def test_format_results_verbose(self):
        checker = MockChecker(self.mock_options(verbose=True))
        self.replay()
        checker.results = {'check_something': ['aaa', 'AAA'],
                           'check_something_else': ['bbb', 'BBB']}
        # Just test the format_results() method doesn't fail, don't
        # make assertions about its result
        checker.format_results()


class TestFilingNumberHelper(FilingNumberMockTestCase):

    def test_get_associated_filing_numbers(self):
        dossier_data = [('FD FDS-Amt-2012-3',  '/dossier3'),
                        ('FD FDS-Amt-2012-1', '/dossier1'),
                        ('FD.FDS-Amt-2012-7', '/dossier7'),
                        ('FD FDS-Xyz-2012-5', '/dossier5'),
                        ('FD.FDS-Amt-2012-2', '/dossier2'),]
        self.mock_catalog(dossier_data)
        self.mock_base_client_id_registry(client_id='FD FDS')
        plone = self.mock_plone()

        self.replay()
        helper = FilingNumberHelper(plone)
        fns = helper.get_associated_filing_numbers('Amt-2012')

        # We expect filing numbers to be sorted correctly
        expected = [('FD FDS-Amt-2012-1', '/dossier1'),
                    ('FD.FDS-Amt-2012-2', '/dossier2'),
                    ('FD FDS-Amt-2012-3', '/dossier3'),
                    ('FD.FDS-Amt-2012-7', '/dossier7')]
        self.assertEquals(fns, expected)

    def test_get_minimal_counter_value(self):
        dossier_data = [('FD FDS-Amt-2012-3',  '/dossier3'),
                        ('FD FDS-Amt-2012-1', '/dossier1'),
                        ('FD.FDS-Amt-2012-7', '/dossier7'),
                        ('FD FDS-Xyz-2012-5', '/dossier5'),
                        ('FD.FDS-Amt-2012-2', '/dossier2'),]
        self.mock_catalog(dossier_data)
        self.mock_base_client_id_registry(client_id='FD FDS')
        plone = self.mock_plone()

        self.replay()
        helper = FilingNumberHelper(plone)
        min_value = helper.get_minimal_counter_value('Amt-2012')
        self.assertEquals(min_value, 7)

    def test_get_filing_number(self):
        self.mock_tool(self.stub(), 'portal_catalog')
        self.mock_base_client_id_registry(client_id='SKA ARCH')

        # Missing IDossierMarker
        dossier = self.mocker.mock()
        plone = self.mock_plone()
        self.replay()
        helper = FilingNumberHelper(plone)
        self.assertRaises(ValueError, helper.get_filing_number, dossier)

        # Test getting the filing number
        self.mocker.reset()

        FNS = ['SKA ARCH-Amt-2012-1',
               'SKA ARCH-Amt-2012-2',
               'SKA ARCH-Amt-2012-3']
        mock_dossiers = []
        for fn in FNS:
            dossier_obj, dossier = self.mock_dossier()
            self.expect(dossier.filing_no).result(fn)
            mock_dossiers.append(dossier_obj)

        self.replay()
        for dossier_obj, fn in zip(mock_dossiers, FNS):
            self.assertEquals(helper.get_filing_number(dossier_obj), fn)

    def test_set_filing_number(self):
        self.mock_tool(self.stub(), 'portal_catalog')
        self.mock_base_client_id_registry(client_id='SKA ARCH')

        # Missing IDossierMarker
        dossier = self.mocker.mock()
        plone = self.mock_plone()
        self.replay()
        helper = FilingNumberHelper(plone)
        self.assertRaises(ValueError, helper.set_filing_number, dossier, None)

        # Test setting a filing number
        self.mocker.reset()
        dossier_obj, dossier = self.mock_dossier()
        FN = 'SKA ARCH-Amt-2012-1'
        dossier.filing_no = FN
        self.expect(dossier_obj.reindexObject())
        self.expect(dossier.filing_no).result(FN)

        self.replay()
        helper.set_filing_number(dossier_obj, FN)
        self.assertEquals(dossier.filing_no, FN)

    def test_get_number_part(self):
        self.mock_tool(self.stub(), 'portal_catalog')
        self.mock_base_client_id_registry(client_id='SKA ARCH')
        plone = self.mock_plone()

        self.replay()
        helper = FilingNumberHelper(plone)
        gnp = helper.get_number_part

        # Number with current prefix
        self.assertEquals(gnp('SKA ARCH-Amt-2012-2'), 2)
        # Numbers with legacy dotted prefix should work as well
        self.assertEquals(gnp('SKA.ARCH-Amt-2012-5'), 5)
        # As should numbers with unknown prefixes
        self.assertEquals(gnp('UNKNOWN-Amt-2012-7'), 7)
        # Subdossier numbers should be dealt with correctly...
        self.assertEquals(gnp('SKA ARCH-Amt-2012-13.7'), 13)
        # in any depth
        self.assertEquals(gnp('SKA ARCH-Amt-2012-13.7.9.1.2.3'), 13)

    def test_get_filing_numbers(self):
        dossier_data = [('FD FDS-Amt-2012-2', '/dossier2'),
                        ('FD FDS-Amt-2012-1', '/dossier1'),
                        ('FD FDS-Xyz-2012-3', '/dossier3'),
                        (None,                '/dossier4'),]
        self.mock_catalog(dossier_data)
        self.mock_base_client_id_registry()
        plone = self.mock_plone()

        self.replay()
        helper = FilingNumberHelper(plone)
        fns = helper.get_filing_numbers()
        # We expect filing numbers to be sorted correctly
        expected = [('FD FDS-Amt-2012-1', '/dossier1'),
                    ('FD FDS-Amt-2012-2', '/dossier2'),
                    ('FD FDS-Xyz-2012-3', '/dossier3')]
        self.assertEquals(fns, expected)

        # Test that filing numbers are memoized after we got them once
        # (brain.getObject() on mock brains shouldn't be called again)
        helper.get_filing_numbers()

    def test_get_filing_number_counters(self):
        counters = {'Amt-2012': self.mock_counter(234),
                    'Xyz-2012': self.mock_counter(4356)}
        self.mock_tool(self.stub(), 'portal_catalog')
        plone = self.mock_plone()
        self.mock_counter_annotations(plone, counters)
        self.mock_base_client_id_registry()

        self.replay()
        helper = FilingNumberHelper(plone)
        counters = helper.get_filing_number_counters()
        self.assertEquals(counters['Amt-2012'].value, 234)
        self.assertEquals(counters['Xyz-2012'].value, 4356)

        # Test that counters are memoized after we got them once
        # (counter annotation_factory() shouldn't be called again)
        helper.get_filing_number_counters()

    def test_get_counter_value(self):
        counters = {'Amt-2012': self.mock_counter(234),
                    'Xyz-2012': self.mock_counter(4356)}
        self.mock_tool(self.stub(), 'portal_catalog')
        plone = self.mock_plone()
        self.mock_counter_annotations(plone, counters)
        self.mock_base_client_id_registry()

        self.replay()
        helper = FilingNumberHelper(plone)
        self.assertEquals(helper.get_counter_value('Amt-2012'), 234)
        self.assertEquals(helper.get_counter_value('Xyz-2012'), 4356)

    def test_get_counter_value_missing_counter(self):
        self.mock_tool(self.stub(), 'portal_catalog')
        plone = self.mock_plone()
        self.mock_counter_annotations(plone, {})
        self.mock_base_client_id_registry()

        self.replay()
        helper = FilingNumberHelper(plone)
        self.assertRaises(ValueError, helper.get_counter_value, 'MISSING-2012')

    def test_set_counter_value(self):
        counter1 = self.mock_counter(123, count=0)
        counter2 = self.mock_counter(123, count=0)
        # Expect our counters to be changed
        counter1.value = 77
        counter2.value = 88
        counters = {'Amt-2012': counter1,
                    'Xyz-2012': counter2}
        self.mock_tool(self.stub(), 'portal_catalog')
        plone = self.mock_plone()
        self.mock_counter_annotations(plone, counters)
        self.mock_base_client_id_registry()

        self.replay()
        helper = FilingNumberHelper(plone)
        helper.set_counter_value('Amt-2012', 77)
        helper.set_counter_value('Xyz-2012', 88)

    def test_set_counter_value_missing_counter(self):
        self.mock_tool(self.stub(), 'portal_catalog')
        plone = self.mock_plone()
        self.mock_counter_annotations(plone, {})
        self.mock_base_client_id_registry()

        self.replay()
        helper = FilingNumberHelper(plone)
        self.assertRaises(ValueError, helper.set_counter_value,
                          'MISSING-2012', 1)

    def test_get_filing_number_counters_missing_annotations(self):
        self.mock_tool(self.stub(), 'portal_catalog')
        self.mock_base_client_id_registry()
        plone = self.mock_plone()

        self.replay()
        helper = FilingNumberHelper(plone)
        self.assertRaises(KeyError, helper.get_filing_number_counters)

    def test_get_filing_number_counters_missing_filing_no_annotation(self):
        """When no annotations are found for FILING_NO_KEY we expect
        get_filing_number_counters() to return an empty dict.
        """
        self.mock_tool(self.stub(), 'portal_catalog')
        # Mock empty annotations
        plone = self.mock_plone()
        annotation_factory = self.mocker.mock()
        self.mock_adapter(annotation_factory, IAnnotations, (Interface,))
        self.expect(annotation_factory(plone)).result({})

        self.mock_base_client_id_registry()

        self.replay()
        helper = FilingNumberHelper(plone)
        counters = helper.get_filing_number_counters()
        self.assertEquals(counters, {})

    def test_get_possible_client_prefixes(self):
        self.mock_tool(self.stub(), 'portal_catalog')
        self.mock_base_client_id_registry('AB CDE')

        # Monkey patch previous client prefixes
        PREVIOUS_CLIENT_PREFIXES = {'ab-cde':  ['PREVIOUS PREFIX']}
        from opengever.dossier import filing_checker
        filing_checker.PREVIOUS_CLIENT_PREFIXES = PREVIOUS_CLIENT_PREFIXES
        plone = self.mock_plone('ab-cde')

        self.replay()
        helper = FilingNumberHelper(plone)
        expected = ['AB CDE', 'AB.CDE', 'PREVIOUS PREFIX']
        self.assertEquals(list(helper.get_possible_client_prefixes()), expected)

    def test_get_possible_client_prefixes_with_current_dotted_prefix(self):
        self.mock_tool(self.stub(), 'portal_catalog')
        self.mock_base_client_id_registry('AB.CDE')
        plone = self.mock_plone('ab-cde')

        # Monkey patch previous client prefixes
        PREVIOUS_CLIENT_PREFIXES = {'ab-cde':  ['PREVIOUS PREFIX']}
        from opengever.dossier import filing_checker
        filing_checker.PREVIOUS_CLIENT_PREFIXES = PREVIOUS_CLIENT_PREFIXES

        self.replay()
        helper = FilingNumberHelper(plone)
        expected = ['AB.CDE', 'PREVIOUS PREFIX']
        self.assertEquals(list(helper.get_possible_client_prefixes()), expected)

    def test_get_prefixless_filing_number(self):
        self.mock_tool(self.stub(), 'portal_catalog')
        self.mock_base_client_id_registry('AB CDE')
        plone = self.mock_plone('ab-cde')

        # Monkey patch previous client prefixes
        PREVIOUS_CLIENT_PREFIXES = {'ab-cde':  ['OLD PREFIX']}
        from opengever.dossier import filing_checker
        filing_checker.PREVIOUS_CLIENT_PREFIXES = PREVIOUS_CLIENT_PREFIXES

        self.replay()
        helper = FilingNumberHelper(plone)
        # For current, dotted and previous prefixes the prefix should be
        # recognized and stripped. For other unknown prefixes the FN
        # is supposed to be returned unchanged.
        expected = {'AB CDE-Amt-2012-7':     'Amt-2012-7',          # current
                    'AB.CDE-Amt-2012-7':     'Amt-2012-7',          # dotted
                    'OLD PREFIX-Amt-2012-7': 'Amt-2012-7',          # previous
                    'UNKNOWN-Amt-2012-7':    'UNKNOWN-Amt-2012-7',  # unknown
        }
        for fn, expected_fn in expected.items():
            self.assertEquals(helper.get_prefixless_filing_number(fn),
                              expected_fn)

    def test_get_filing_key_from_filing_number(self):
        self.mock_tool(self.stub(), 'portal_catalog')
        self.mock_base_client_id_registry('AB CDE')
        plone = self.mock_plone('ab-cde')

        # Monkey patch previous client prefixes
        PREVIOUS_CLIENT_PREFIXES = {'ab-cde':  ['OLD PREFIX']}
        from opengever.dossier import filing_checker
        filing_checker.PREVIOUS_CLIENT_PREFIXES = PREVIOUS_CLIENT_PREFIXES

        self.replay()
        helper = FilingNumberHelper(plone)

        expected = {'AB CDE-Amt-2012-7':     'Amt-2012',    # current CP
                    'AB.CDE-Amt-2012-7':     'Amt-2012',    # dotted CP
                    'Amt-2012-7':            'Amt-2012',    # missing CP
                    'OLD PREFIX-Amt-2012-7': 'Amt-2012',    # previous CP
                    }
        for fn, expected_fn in expected.items():
            self.assertEquals(helper.get_filing_key_from_filing_number(fn),
                              expected_fn)

        # Filing number with unknown client prefix should raise ValueError
        self.assertRaises(ValueError, helper.get_filing_key_from_filing_number,
                          'UNKNOWN-Amt-2012-7')


class TestFilingNumberChecker(FilingNumberMockTestCase):

    def test_duplicates(self):
        dossier_data = [('SKA ARCH-Amt-2012-1', '/dossier1'),  # duplicate
                        ('SKA ARCH-Amt-2012-1', '/dossier2'),  # duplicate
                        ('SKA ARCH-Amt-2012-7', '/dossier3')]  # OK
        self.mock_catalog(dossier_data)
        self.mock_base_client_id_registry()
        plone = self.mock_plone()

        self.replay()
        checker = FilingNumberChecker(self.options, plone)
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
        plone = self.mock_plone()

        self.replay()
        checker = FilingNumberChecker(self.options, plone)
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
        plone = self.mock_plone()

        self.replay()
        checker = FilingNumberChecker(self.options, plone)
        checker.legacy_prefixes = {u'Finanzdirektion': u'Direktion'}
        results = checker.check_for_legacy_filing_prefixes()
        self.assertEquals(results, [('Finanzdirektion-2012-1', '/dossier1')])

    def test_missing_client_prefixes(self):
        dossier_data = [('Amt-2012-1',          '/dossier1'),  # missing prefix
                        ('SKA ARCH-Amt-2012-2', '/dossier2'),  # OK
                        ('FD FDS-Amt-2012-3',   '/dossier3')]  # wrong client
        self.mock_catalog(dossier_data)
        self.mock_base_client_id_registry('SKA ARCH')
        plone = self.mock_plone()

        self.replay()
        checker = FilingNumberChecker(self.options, plone)
        results = checker.check_for_missing_client_prefixes()
        self.assertEquals(results, [('Amt-2012-1',        '/dossier1'),
                                    ('FD FDS-Amt-2012-3', '/dossier3')])

    def test_dotted_client_prefixes(self):
        dossier_data = [('FD FDS-Amt-2012-1', '/dossier1'),  # OK
                        ('FD.FDS-Amt-2012-2', '/dossier2'),  # dotted prefix
                        ('OTHER-Amt-2012-1', '/dossier3'),   # OK
                        ]
        self.mock_catalog(dossier_data)
        self.mock_base_client_id_registry(client_id='FD FDS')
        plone = self.mock_plone()

        self.replay()
        checker = FilingNumberChecker(self.options, plone)
        results = checker.check_for_dotted_client_prefixes()
        self.assertEquals(results, [('FD.FDS-Amt-2012-2', '/dossier2')])

    def test_dotted_client_prefixes_no_space_in_current_prefix(self):
        self.mock_catalog([])
         # If current client prefix doesn't contain a space, there are
         # (by definition) no dotted prefixes
        self.mock_base_client_id_registry(client_id='NOSPACE')
        plone = self.mock_plone()

        self.replay()
        checker = FilingNumberChecker(self.options, plone)
        results = checker.check_for_dotted_client_prefixes()
        self.assertEquals(results, [])

    def test_bad_counters(self):
        counters = {'Amt-2012': self.mock_counter(77, count=2),
                    'Xyz-2012': self.mock_counter(99),
                    'ABC-2012': self.mock_counter(1, count=0)}
        dossier_data = [('FD FDS-Amt-2012-1',  '/dossier1'),  # OK
                        ('FD FDS-Amt-2012-78', '/dossier2'),  # too high
                        ('FD FDS-Xyz-2012-99', '/dossier3')]  # OK
        plone = self.mock_plone()
        self.mock_catalog(dossier_data)
        self.mock_counter_annotations(plone, counters)
        self.mock_base_client_id_registry(client_id='FD FDS')

        self.replay()
        checker = FilingNumberChecker(self.options, plone)
        results = checker.check_for_bad_counters()

        # Test we don't get an Increaser instance back, but an integer
        self.assertIsInstance(results[0][1], int)

        expected = [('Amt-2012', 77, 'FD FDS-Amt-2012-78')]
        self.assertEquals(results, expected)

    def test_counters_needing_initialization(self):
        counters = {'Amt-2012': self.mock_counter(77),
                    'Xyz-2012': self.mock_counter(0),}
        dossier_data = [('FD FDS-Amt-2012-1',  '/dossier1'),
                        ('FD FDS-Xyz-2012-1',  '/dossier2'),
                        ('FD FDS-ABC-2012-1',  '/dossier3')]
        plone = self.mock_plone()
        self.mock_catalog(dossier_data)
        self.mock_counter_annotations(plone, counters)
        self.mock_base_client_id_registry(client_id='FD FDS')

        self.replay()
        checker = FilingNumberChecker(self.options, plone)
        results = checker.check_for_counters_needing_initialization()

        expected = [('ABC-2012', '( 1 dossiers)'),
                    ('Xyz-2012', '( 1 dossiers)')]
        self.assertEquals(results, expected)
