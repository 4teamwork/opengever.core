from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from five import grok
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from ftw.table import helper
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.dossier import _ as _dossier
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.browser.participants import role_list_helper
from opengever.latex.utils import get_issuer_of_task
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_client
from opengever.repository.interfaces import IRepositoryFolder
from opengever.tabbedview.helper import readable_ogds_author
from opengever.latex.utils import workflow_state
from opengever.task.helper import task_type_helper
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import Interface
from zope.schema import vocabulary


class IDossierDetailsLayer(Interface):
    """Request layer for selecting the dossier details view.
    """


class DossierDetailsPDFView(grok.View, ExportPDFView):
    grok.name('pdf-dossier-details')
    grok.context(IDossierMarker)
    grok.require('zope2.View')

    def render(self):
        # Enable IDossierDetailsLayer
        provide_request_layer(self.request, IDossierDetailsLayer)

        return ExportPDFView.__call__(self)


class DossierDetailsLaTeXView(grok.MultiAdapter, MakoLaTeXView):
    grok.provides(ILaTeXView)
    grok.adapts(Interface, IDossierDetailsLayer, ILaTeXLayout)

    template_directories = ['templates']
    template_name = 'dossierdetails.tex'

    def get_render_arguments(self):
        self.layout.show_contact = False

        args = self.get_dossier_metadata()

        parent = aq_parent(aq_inner(self.context))
        args['is_subdossier'] = IDossierMarker.providedBy(parent)

        args['participants'] = self.get_participants()
        args['tasks'] = self.get_tasks()
        args['documents'] = self.get_documents()
        args['subdossiers'] = self.get_subdossiers()

        self.layout.use_package('pdflscape')
        self.layout.use_package('longtable')

        return args

    def get_dossier_metadata(self):
        dossier = IDossier(self.context)
        client = get_current_client()
        info = getUtility(IContactInformation)

        args = {}

        parent = aq_parent(aq_inner(self.context))
        if IDossierMarker.providedBy(parent):
            args['title_dossier'] = parent.Title()
            args['title_subdossier'] = self.context.Title()
        else:
            args['title_dossier'] = self.context.Title()

        args['repository'] = self.get_repository_path()
        args['start'] = helper.readable_date(self.context, dossier.start)
        args['end'] = helper.readable_date(self.context, dossier.end)

        state = self.context.restrictedTraverse('@@plone_context_state')
        args['review_state'] = translate(state.workflow_state(),
                                         domain='plone',
                                         context=self.request)

        args['responsible'] = '%s / %s' % (
            (client.title, info.describe(dossier.responsible)))

        args['reference'] = IReferenceNumber(self.context).get_number()

        seq = getUtility(ISequenceNumber)
        args['sequence'] = seq.get_number(self.context)

        args['filing_no'] = getattr(dossier, 'filing_no', None)
        args['filingprefix'] = self.get_filingprefix()

        return self.convert_dict(args)

    def get_filingprefix(self):
        value = IDossier(self.context).filing_prefix

        if value:
            # Get the value and not the key from the prefix vocabulary
            voc = vocabulary.getVocabularyRegistry().get(
                self.context, 'opengever.dossier.type_prefixes')

            return voc.by_token.get(value).title

        else:
            return ''

    def get_repository_path(self):
        """Returns a reverted, path-like list of parental repository folder
        titles, not including the dossier itself nor the repository root,
        seperated by slashes.
        """

        titles = []

        obj = self.context

        while not IPloneSiteRoot.providedBy(obj):
            if IRepositoryFolder.providedBy(obj):
                titles.append(obj.Title())

            obj = aq_parent(aq_inner(obj))

        return ' / '.join(self.convert_list(titles))

    def get_participants(self):
        dossier = IDossier(self.context)
        rows = []

        # add the responsible
        rows.append('%s, %s' % (
                readable_ogds_author(None, dossier.responsible),
                translate(_dossier(u'label_responsible', 'Responsible'),
                          context=self.request)))

        # add the participants
        participants = list(IParticipationAware(
                self.context).get_participations())

        for participant in participants:
            rows.append('%s, %s' % (
                    readable_ogds_author(participant, participant.contact),
                    role_list_helper(participant, participant.roles)))

        return self.convert_list(rows)

    def _get_sorted_results(self, tab_name, markers):
        """Returns the results of a catalog query for objects that provide
        any of the markers and sorts the using the sort options last used
        in the tabbed view tab tab_name, applying any custom methods if
        necessary.
        """
        # read the sort_on and sort_order attributes from the gridstate
        tab = self.context.restrictedTraverse('tabbedview_view-%s' % tab_name)
        tab.table_options = {}
        tab.load_grid_state()

        sort_on = tab.sort_on
        sort_order = 'descending'
        if tab.sort_order == 'asc':
            sort_order = 'ascending'

        sort_reverse = 1
        if sort_order == 'ascending':
            sort_reverse = 0

        catalog = getToolByName(self.context, 'portal_catalog')
        query = {'path': '/'.join(self.context.getPhysicalPath()),
                'object_provides': markers}

        query = tab.table_source.extend_query_with_ordering(query)

        brains = catalog(query)

        # Apply any custom sort methods to results if necessary
        brains = tab.custom_sort(brains, sort_on, sort_reverse)
        return brains

    def get_tasks(self):
        info = getUtility(IContactInformation)
        rows = []

        markers = ['opengever.task.task.ITask']
        brains = self._get_sorted_results('tasks', markers)

        for brain in brains:
            issuer = get_issuer_of_task(brain, with_client=True,
                                        with_principal=False)

            responsible = '%s / %s' %  (
                info.get_client_by_id(brain.assigned_client).title,
                info.describe(brain.responsible, with_principal=False))

            data = [
                brain.sequence_number,
                task_type_helper(brain, brain.task_type),
                issuer,
                responsible,
                workflow_state(brain, brain.review_state),
                brain.Title,
                helper.readable_date(brain, brain.deadline)]

            rows.append(self.convert_list_to_row(data))

        return rows

    def get_documents(self):
        rows = []

        documents_marker = 'opengever.document.document.IDocumentSchema'
        mail_marker = 'ftw.mail.mail.IMail'
        markers = [documents_marker, mail_marker]
        brains = self._get_sorted_results('documents', markers)

        for brain in brains:
            data = [brain.sequence_number,
                    brain.Title,
                    helper.readable_date(brain, brain.document_date),
                    helper.readable_date(brain, brain.receipt_date),
                    helper.readable_date(brain, brain.delivery_date),
                    brain.document_author]

            rows.append(self.convert_list_to_row(data))

        return rows

    def get_subdossiers(self):
        info = getUtility(IContactInformation)
        rows = []

        markers = ['opengever.dossier.behaviors.dossier.IDossierMarker']
        brains = self._get_sorted_results('subdossiers', markers)

        context_path = '/'.join(self.context.getPhysicalPath())

        for brain in brains:
            if brain.getPath() == context_path:
                continue

            data = [
                brain.sequence_number,
                brain.filing_no,
                brain.Title,
                info.describe(brain.responsible),
                workflow_state(brain, brain.review_state),
                helper.readable_date(brain, brain.start),
                helper.readable_date(brain, brain.end)]

            rows.append(self.convert_list_to_row(data))

        return rows

    def convert_list_to_row(self, data):
        return ' & '.join(self.convert_list(data))

    def convert_list(self, items):
        """Returns a new list, containing all values in `items` convertend
        into LaTeX.
        """
        data = []

        for item in items:
            if item is None:
                item = ''

            if isinstance(item, unicode):
                item = item.encode('utf-8')

            if not isinstance(item, str):
                item = str(item)

            data.append(self.convert_plain(item))

        return data

    def convert_dict(self, data):
        """Returns a new dict where all values of the dict `data` are
        converted into LaTeX.
        """
        return dict(zip(data.keys(), self.convert_list(data.values())))
