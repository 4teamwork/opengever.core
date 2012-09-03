from ftw.testing import MockTestCase
from ftw.testing.layer import ComponentRegistryLayer
from opengever.base.interfaces import IBaseClientID
from opengever.dossier.archive import FILING_NO_KEY
from opengever.dossier.behaviors.dossier import IDossier, IDossierMarker
from opengever.dossier.filing_checker import FilingNumberChecker
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
