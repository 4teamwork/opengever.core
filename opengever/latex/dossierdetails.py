from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.mail.mail import IMail
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from ftw.table import helper
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.document.document import IDocumentSchema
from opengever.dossier import _ as _dossier
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.browser.participants import role_list_helper
from opengever.globalindex.model.task import Task
from opengever.latex import _
from opengever.latex.listing import ILaTexListing
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.repository.interfaces import IRepositoryFolder
from opengever.tabbedview.helper import readable_ogds_author
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import Interface


class IDossierDetailsLayer(Interface):
    """Request layer for selecting the dossier details view.
    """


class DossierDetailsPDFView(ExportPDFView):

    request_layer = IDossierDetailsLayer

    def __call__(self):
        # Enable IDossierDetailsLayer
        provide_request_layer(self.request, self.request_layer)

        return super(DossierDetailsPDFView, self).__call__()


@adapter(Interface, IDossierDetailsLayer, ILaTeXLayout)
class DossierDetailsLaTeXView(MakoLaTeXView):

    template_directories = ['templates']
    template_name = 'dossierdetails.tex'

    def get_render_arguments(self):
        self.layout.show_contact = False

        args = {'dossier_metadata': self.get_dossier_metadata()}

        parent = aq_parent(aq_inner(self.context))
        args['is_subdossier'] = IDossierMarker.providedBy(parent)

        args['participants'] = self.get_participants()

        # subdossiers
        args['subdossierstitle'] = translate(
            _('label_subdossiers', default="Subdossiers"), context=self.request)

        listing = getMultiAdapter((self.context, self.request, self),
                                  ILaTexListing, name='subdossiers')
        args['subdossiers'] = listing.get_listing(self.get_subdossiers())

        # documents
        args['documentstitle'] = translate(
            _('label_documents', default="Documents"), context=self.request)

        listing = getMultiAdapter((self.context, self.request, self),
                                  ILaTexListing, name='documents')
        args['documents'] = listing.get_listing(self.get_documents())

        # tasks
        args['taskstitle'] = translate(
            _('label_tasks', default="Tasks"), context=self.request)

        listing = getMultiAdapter(
            (self.context, self.request, self), ILaTexListing, name='tasks')
        args['tasks'] = listing.get_listing(self.get_tasks())

        self.layout.use_package('pdflscape')
        self.layout.use_package('longtable')

        return args

    def get_metadata_order(self):
        return ['reference', 'sequence', 'repository', 'title',
                'subdossier_title', 'state', 'responsible',
                'participants', 'start', 'end']

    def get_metadata_config(self):
        return {
            'reference': {
                'label': _('label_reference_number',
                           default='Reference number'),
                'getter': self.get_reference_number},
            'sequence': {
                'label': _('label_sequence_number', default='Sequence number'),
                'getter': self.get_sequence_number},
            'repository': {
                'label': _('label_repository', default='Repository'),
                'getter': self.get_repository_path},
            'title': {
                'label': _('label_title', default='Title'),
                'getter': self.get_title},
            'subdossier_title': {
                'label': _('label_subdossier_title', default='Subdossier Title'),
                'getter': self.get_subdossier_title},
            'responsible': {
                'label': _('label_responsible', default='Responsible'),
                'getter': self.get_responsible},
            'start': {
                'label': _('label_start', default='Start'),
                'getter': self.get_start_date},
            'end': {
                'label': _('label_end', default='End'),
                'getter': self.get_end_date},
            'participants': {
                'label': _('label_participants', default='Participants'),
                'getter': self.get_participants,
                'is_latex': True},
            'state': {
                'label': _('label_review_state', default='State'),
                'getter': self.get_review_state}}

    def get_dossier_metadata(self):
        rows = []
        config = self.get_metadata_config()

        for key in self.get_metadata_order():
            row = config.get(key)

            value = row.get('getter')()
            if not value:
                continue
            if not row.get('is_latex'):
                value = self.convert_plain(value)

            label = translate(row.get('label'), context=self.request)
            rows.append('\\bf {} & {} \\\\%%'.format(
                self.convert_plain(label), value))

        return '\n'.join(rows)

    def get_reference_number(self):
        return IReferenceNumber(self.context).get_number()

    def get_sequence_number(self):
        return str(getUtility(ISequenceNumber).get_number(self.context))

    def get_title(self):
        if self.context.is_subdossier():
            return aq_parent(aq_inner(self.context)).Title()
        return self.context.Title()

    def get_subdossier_title(self):
        if self.context.is_subdossier():
            return self.context.Title()
        return None

    def get_review_state(self):
        state = self.context.restrictedTraverse('@@plone_context_state')
        return translate(state.workflow_state(), domain='plone',
                         context=self.request)

    def get_start_date(self):
        return helper.readable_date(
            self.context, IDossier(self.context).start)

    def get_end_date(self):
        return helper.readable_date(
            self.context, IDossier(self.context).end)

    def get_responsible(self):
        return self.context.get_responsible_actor().get_label_with_admin_unit()

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

        return ' / '.join(titles)

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

        values = ['{', '\\vspace{-\\baselineskip}\\begin{itemize}']
        for row in self.convert_list(rows):
            values.append('\\item {}'.format(row))

        values.append('\\vspace{-\\baselineskip}\\end{itemize}')
        values.append('}')

        return ' \n'.join(values)

    def get_subdossiers(self):
        sort_on, sort_order = self.get_sorting('subdossiers')
        return self.context.get_subdossiers(
            sort_on=sort_on, sort_order=sort_order)

    def get_tasks(self):
        return Task.query.by_container(self.context,
                                       get_current_admin_unit())\
                         .order_by(Task.sequence_number)\
                         .all()

    def get_documents(self):
        sort_on, sort_order = self.get_sorting('documents')
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'path': '/'.join(self.context.getPhysicalPath()),
            'object_provides': [IDocumentSchema.__identifier__,
                                IMail.__identifier__]}

        return catalog(query)

    def get_sorting(self, tab_name):
        """Read the sort_on and sort_order attributes from the gridstate,
        for the given tab and returns them"""

        tab = self.context.restrictedTraverse('tabbedview_view-%s' % tab_name)
        tab.table_options = {}
        tab.load_grid_state()

        sort_on = tab.sort_on
        sort_order = 'descending'
        if tab.sort_order == 'asc':
            sort_order = 'ascending'

        return sort_on, sort_order

    def convert_list(self, items):
        """Returns a new list, containing all values in `items` converted
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
