from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from datetime import datetime
from ftw.testing import MockTestCase
from opengever.base.interfaces import IBaseClientID
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
from opengever.latex.dossiercover import DossierCoverPDFView
from opengever.latex.testing import LATEX_ZCML_LAYER
from opengever.ogds.base.interfaces import IContactInformation
from opengever.repository.interfaces import IRepositoryFolder
from plone.registry.interfaces import IRegistry
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

    def stub_tree(self):
        tree = self.create_dummy()
        tree.subdossier = self.providing_stub([IDossierMarker])
        tree.dossier = self.providing_stub([IDossierMarker])
        tree.subfolder = self.providing_stub([IRepositoryFolder])
        tree.folder = self.providing_stub([IRepositoryFolder])
        tree.repository = self.stub()
        tree.site = self.providing_stub([IPloneSiteRoot])

        self.expect(tree.subdossier.toLocalizedTime).result(
            toLocalizedTime)

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

        # filingprefix
        self.expect(IDossier(context_mock).filing_prefix).result('PREFIX')
        voc = self.mocker.mock()
        self.expect(self.getVocabularyRegistry().get(
                context_mock, 'opengever.dossier.type_prefixes')).result(voc)
        self.expect(voc.by_token.get('PREFIX').title).result(defaults.get(
                'filingprefix'))

        # filing nr
        self.expect(IDossier(context_mock).filing_no).result(
            defaults.get('filingnr'))

        # sequence nr
        seq_utility = self.mocker.mock()
        self.mock_utility(seq_utility, ISequenceNumber)
        self.expect(seq_utility.get_number(context_mock)).result(
            defaults.get('sequencenr'))

        # title / description / dastes
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

    def test_get_reversed_breadcrumbs(self):
        tree = self.stub_tree()

        context = tree.subdossier

        request = self.stub()

        self.replay()

        view = DossierCoverPDFView(context, request)

        self.assertEqual(view.get_reversed_breadcrumbs(),
                         'Sub Folder / Folder')

    def test_get_render_arguments(self):
        tree = self.stub_tree()
        context = tree.subdossier
        self.mock_metadata(context)
        request = self.stub()

        self.replay()

        view = DossierCoverPDFView(context, request)

        self.assertEqual(
            view.get_render_arguments(),

            {'clientid': 'OG',
             'repository': 'Sub Folder / Folder',
             'referencenr': 'OG 1.6 / 1',
             'filingprefix': 'Leitung',
             'parentDossierTitle': 'Dossier title',
             'filingnr': '5',
             'sequencenr': '2',
             'title': 'My Dossier',
             'description': 'The description',
             'responsible': 'John Doe',
             'start': '2011-09-24 00:00:00',
             'end': '2011-11-22 00:00:00'})

    def test_description_cutting(self):
        dossier = self.stub()
        request = self.stub()

        small_title = 'Lorem ipsum dolor sit amet'
        long_title = 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor in- vidunt ut labore et dolore magna aliquy'

        # a to long description wuthout any linebreaks
        description_1 = 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor in- vidunt ut labore et dolore magna aliquyam erat, sed diam volup- tua. At ve- ro eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ip- sum dolor sit amet. Lorem ipsum dolor Lorem ipsum dolor sit amet consetetur, sadipscing elitr, sed diam nonumy eirmod tempor in- vidunt ut laboree et dolore magna aliquyam erat, sed diam volup- tua.'

        cutted_description_1 = 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor in- vidunt ut labore et dolore magna aliquyam erat, sed diam volup- tua. At ve- ro eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ip- sum dolor sit amet. Lorem ipsum ...'

        # a description with to many lines
        description_2 = """Lorem ipsum dolor sit amet:
 - consetetur sadipscing
 - elitr
 - sed diam nonumy eirmod
 - tempor in
 - vidunt ut labore et dolore magna
 - aliquyam erat, sed diam
 - volup- tua.
 - At ve- ro eos et accusam et
 - justo duo dolores et ea rebum.
 - Stet clita kasd gubergren, no sea
 - takimata sanctus est Lorem ip"""

        cutted_description_2 = """Lorem ipsum dolor sit amet:<br /> - consetetur sadipscing<br /> - elitr<br /> - sed diam nonumy eirmod<br /> - tempor in<br /> - vidunt ut labore et dolore magna<br /> - aliquyam erat, sed diam ..."""

        # a description with to many long lines
        description_3 = """Lorem ipsum dolor sit amet:
 - Lorem ipsum dolor sit amet, consetetur sadipscing elitr
 - Lorem ipsum dolor sit amet, consetetur sadipscing elitr
 - Lorem ipsum dolor sit amet, consetetur sadipscing elitr
 - Lorem ipsum dolor sit amet, consetetur sadipscing elitr
 - Lorem ipsum dolor sit amet, consetetur sadipscing elitr
 - Lorem ipsum dolor sit amet, consetetur sadipscing elitr
 - Lorem ipsum dolor sit amet, consetetur sadipscing elitr
 - Lorem ipsum dolor sit amet, consetetur sadipscing elitr
"""

        cutted_description_3 = """Lorem ipsum dolor sit amet:<br /> - Lorem ipsum dolor sit amet, consetetur sadipscing elitr<br /> - Lorem ipsum dolor sit amet, consetetur sadipscing elitr<br /> - Lorem ipsum dolor sit amet, consetetur sadipscing elitr ..."""

        # a description with to many lines and a to long title
        cutted_description_4 = """Lorem ipsum dolor sit amet:<br /> - consetetur sadipscing<br /> - elitr<br /> - sed diam nonumy eirmod ..."""

        with self.mocker.order():
            self.expect(dossier.Description()).result(description_1)
            self.expect(dossier.Title()).result(small_title)

            self.expect(dossier.Description()).result(description_2)
            self.expect(dossier.Title()).result(small_title)

            self.expect(dossier.Description()).result(description_3)
            self.expect(dossier.Title()).result(small_title)

            self.expect(dossier.Title()).result(description_2)
            self.expect(dossier.Title()).result(long_title)

        self.replay()

        view = DossierCoverPDFView(dossier, request)
        self.assertEquals(view.get_description(), cutted_description_1)
        self.assertEquals(view.get_description(), cutted_description_2)
        self.assertEquals(view.get_description(), cutted_description_3)
