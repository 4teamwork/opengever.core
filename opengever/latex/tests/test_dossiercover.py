from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from datetime import datetime
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testing import MockTestCase
from opengever.base.interfaces import IBaseClientID
from opengever.base.interfaces import IReferenceNumber
from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
from opengever.latex.dossiercover import IDossierCoverLayer
from opengever.latex.testing import LATEX_ZCML_LAYER
from opengever.ogds.base.interfaces import IContactInformation
from opengever.repository.interfaces import IRepositoryFolder
from opengever.repository.repositoryroot import IRepositoryRoot
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.schema import vocabulary


def toLocalizedTime(arg):
    return arg


class TestDossierCoverPDFView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def setUp(self):
        super(TestDossierCoverPDFView, self).setUp()
        # mock vocabulary registry
        if not hasattr(self, '_ori_getVocReg'):
            self._ori_getVocReg = vocabulary.getVocabularyRegistry
        self.getVocabularyRegistry = self.mocker.replace(
            'zope.schema.vocabulary.getVocabularyRegistry')

    def tearDown(self):
        super(TestDossierCoverPDFView, self).tearDown()
        vocabulary.getVocabularyRegistry = self._ori_getVocReg
        self.getVocabularyRegistry = None

    def stub_tree(self, long_title=False):
        tree = self.create_dummy()
        tree.subdossier = self.providing_stub([IDossierMarker])
        tree.dossier = self.providing_stub([IDossierMarker])
        tree.subfolder = self.providing_stub([IRepositoryFolder])
        tree.folder = self.providing_stub([IRepositoryFolder])
        tree.repository = self.providing_stub([IRepositoryRoot])
        tree.site = self.providing_stub([IPloneSiteRoot])

        self.expect(tree.subdossier.toLocalizedTime).result(
            toLocalizedTime)
        self.expect(tree.repository.version).result('Repository 2.0 2013')

        if long_title:
            self.expect(tree.subfolder.Title()).result(10 * 'Lorem ipsum subfolder ')
            self.expect(tree.folder.Title()).result(10 * 'Lorem ipsum folder ')
            self.expect(tree.dossier.Title()).result(10 * 'Lorem ipsum dossier ')
        else:
            self.expect(tree.subfolder.Title()).result('Sub Folder')
            self.expect(tree.folder.Title()).result('Folder')
            self.expect(tree.dossier.Title()).result('Dossier title')

        self.set_parent(
            tree.subdossier, self.set_parent(
                tree.dossier, self.set_parent(
                    tree.subfolder, self.set_parent(
                        tree.folder, self.set_parent(
                            tree.repository,
                            tree.site)))))

        return tree

    def mock_metadata(self, context_mock, metadata=None):
        defaults = {
            'clientid': 'OG',
            'referencenr': 'OG 1.6 / 1',
            'filingprefix': 'Leitung',
            'filingnr': '5',
            'sequencenr': '2',
            'title': 'My Dossier',
            'description': 'The description',
            'responsible': 'John Doe',
            'start': datetime(2011, 9, 24),
            'end': datetime(2011, 11, 22)}

        if metadata:
            defaults.update(metadata)

        # clientid
        registry = self.mocker.mock()
        self.expect(registry.forInterface(IBaseClientID).client_id).result(
            defaults.get('clientid'))
        self.mock_utility(registry, IRegistry)

        # referencenr
        ref_adapter = self.mocker.mock()
        self.mock_adapter(ref_adapter, IReferenceNumber, [IDossierMarker])
        self.expect(ref_adapter(context_mock).get_number()).result(
            defaults.get('referencenr'))

        # title / description
        self.expect(context_mock.Title()).result(defaults.get('title'))
        self.expect(context_mock.Description()).result(
            defaults.get('description'))

        # responsible
        self.expect(IDossier(context_mock).responsible).result('RESPONSIBLE')
        info_utility = self.mocker.mock()
        self.mock_utility(info_utility, IContactInformation)
        self.expect(info_utility.describe('RESPONSIBLE')).result(
            defaults.get('responsible'))

        # start / end
        self.expect(IDossier(context_mock).start).result(
            defaults.get('start'))
        self.expect(IDossier(context_mock).end).result(
            defaults.get('end'))

        # client_title
        registry_mock = self.stub()
        self.expect(
            registry_mock.forInterface(IBaseClientID).client_title).result('FAKE Client')
        self.mock_utility(registry_mock, IRegistry)

    def mock_converter(self, layout):
        converter = self.stub()
        self.expect(layout.get_converter()).result(converter)
        self.expect(
            converter.convert_plain('FAKE Client')).result('conv:FAKE Client')
        self.expect(
            converter.convert_plain('Repository 2.0 2013')).result(
                'conv:Repository 2.0 2013')
        self.expect(
            converter.convert_plain('referencenr')).result('conv:OG 1.6 / 1')
        self.expect(
            converter.convert_plain('My Dossier')).result('conv:My Dossier')
        self.expect(
            converter.convert('The description')).result('conv:The description')
        self.expect(
            converter.convert_plain('John Doe')).result('conv:John Doe')
        self.expect(
            converter.convert_plain('OG 1.6 / 1')).result('conv:OG 1.6 / 1')
        self.expect(
            converter.convert_plain('2011-09-24 00:00:00')).result(
                'conv:2011-09-24 00:00:00')
        self.expect(
            converter.convert_plain('2011-11-22 00:00:00')).result(
                'conv:2011-11-22 00:00:00')

    def test_get_render_arguments(self):
        tree = self.stub_tree()
        context = tree.subdossier
        self.mock_metadata(context)
        request = self.providing_stub([IDossierCoverLayer])
        layout = self.providing_stub([ILaTeXLayout])
        self.mock_converter(layout)

        self.replay()
        view = getMultiAdapter((context, request, layout), ILaTeXView)

        self.assertEqual(
            view.get_render_arguments(),

            {'clienttitle': 'conv:FAKE Client',
             'referencenr': 'conv:OG 1.6 / 1',
             'repositoryversion': 'conv:Repository 2.0 2013',
             'title': 'conv:My Dossier',
             'description': 'conv:The description',
             'responsible': 'conv:John Doe',
             'start': 'conv:2011-09-24 00:00:00',
             'end': 'conv:2011-11-22 00:00:00'})
