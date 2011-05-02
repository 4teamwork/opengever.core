from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.dossier import _ as _dossier
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.browser.participants import role_list_helper
from opengever.latex.template import LatexTemplateFile
from opengever.latex.views.baselisting import BasePDFListing
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_client
from opengever.repository.interfaces import IRepositoryFolder
from opengever.tabbedview.helper import readable_ogds_author
from opengever.tabbedview.helper import readable_date
from opengever.task.helper import task_type_helper
from zope.component import getUtility


class DossierDetailsPDF(BasePDFListing):
    """Create a PDF with dossier details.
    """

    main = LatexTemplateFile('dossierdetails_main.tex')
    tasks = LatexTemplateFile('dossierdetails_tasks.tex')
    documents = LatexTemplateFile('dossierdetails_documents.tex')
    subdossiers = LatexTemplateFile('dossierdetails_subdossiers.tex')

    def render(self):
        return self.main(tasks=self.get_tasks_latex(),
                         documents=self.get_documents_latex(),
                         subdossiers=self.get_subdossiers_latex(),
                         participation=self.get_participants_latex(),
                         **self.get_main_options())

    def get_main_options(self):
        """Returns a dict of options for the main details table.
        """

        client = get_current_client()
        info = getUtility(IContactInformation)
        data = {}

        dossier = IDossier(self.context)

        data['reference'] = IReferenceNumber(self.context).get_number()
        seq = getUtility(ISequenceNumber)
        data['sequence'] = str(seq.get_number(self.context))
        data['filing_no'] = str(getattr(self.context, 'filing_no', ''))

        # buildout a kind of breadcrumbs with all parental repository folders
        repository = []
        parent = aq_parent(aq_inner(self.context))
        while not IPloneSiteRoot.providedBy(parent):
            if IRepositoryFolder.providedBy(parent):
                repository.append(parent.Title())
            parent = aq_parent(aq_inner(parent))

        data['repository'] = ' / '.join(repository)

        data['title'] = self.context.Title()
        state = self.context.restrictedTraverse('@@plone_context_state')
        data['review_state'] = self.context.translate(state.workflow_state(),
                                                      domain='plone')

        data['responsible'] = ' '.join(
            (str(client.title), '/', info.describe(dossier.responsible)))

        data['start'] = readable_date(self.context, dossier.start)
        data['end'] = readable_date(self.context, dossier.end)

        # convert to latex
        return dict([(key, self.convert(value))
                     for key, value in data.items()])

    def get_participants_latex(self):
        """Get a LaTeX listing of participants.
        """

        # get effective participants
        phandler = IParticipationAware(self.context)
        participants = list(phandler.get_participations())

        # also append the responsible
        class ResponsibleParticipant(object): pass

        responsible = ResponsibleParticipant()
        responsible.roles = _dossier(u'label_responsible', 'Responsible')
        responsible.role_list = responsible.roles

        dossier_adpt = IDossier(self.context)
        responsible.contact = dossier_adpt.responsible
        participants.append(responsible)

        # sort the list
        participants.sort(lambda a, b: cmp(getattr(a, 'contact', ''),
                                           getattr(b, 'contact', '')))

        # generate latex
        latex = [r'{\vspace{-\baselineskip}\begin{itemize}']

        for participant in participants:
            row = '%s, %s' % (
                readable_ogds_author(participant, participant.contact),
                role_list_helper(participant, participant.roles))
            latex.append(r'\item %s' % self.convert(row))

        latex.append(r'\vspace{-\baselineskip}\end{itemize}}')

        return '\n'.join(latex)

    def get_tasks_latex(self):
        """Returns the latex containing all tasks which are within
        this dossier - or an empty string if there are none.
        """

        rows = []
        task_marker = 'opengever.task.task.ITask'

        # make the query
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog({'path': '/'.join(self.context.getPhysicalPath()),
                          'object_provides': task_marker})

        # any results?
        if len(brains) == 0:
            return ''

        info = getUtility(IContactInformation)

        # create rows in latex
        for brain in brains:

            rows.append(self._prepare_table_row(
                    unicode(brain.sequence_number).encode('utf-8'),
                    task_type_helper(brain, brain.task_type),
                    info.describe(brain.issuer),
                    info.describe(brain.responsible),
                    self.context.translate(brain.review_state,
                                           domain='plone'),
                    unicode(brain.Title).encode('utf-8'),
                    readable_date(brain, brain.deadline),
                    ))

        return self.tasks(rows=''.join(rows))

    def get_documents_latex(self):
        """Returns the latex containing all documents which are within
        this dossier - or an empty string if there are none.
        """

        rows = []
        documents_marker = 'opengever.document.document.IDocumentSchema'

        # make the query
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog({'path': '/'.join(self.context.getPhysicalPath()),
                          'object_provides': documents_marker})

        # any results?
        if len(brains) == 0:
            return ''

        # create rows in latex
        for brain in brains:

            rows.append(self._prepare_table_row(
                    unicode(brain.sequence_number).encode('utf-8'),
                    unicode(brain.Title).encode('utf-8'),
                    readable_date(brain, brain.document_date),
                    ))

        return self.documents(rows=''.join(rows))

    def get_subdossiers_latex(self):
        """Returns the latex containing all subdossiers which are within
        this dossier - or an empty string if there are none.
        """

        rows = []
        dossier_marker = 'opengever.dossier.behaviors.dossier.IDossierMarker'

        # make the query
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog({'path': '/'.join(self.context.getPhysicalPath())+'/',
                          'object_provides': dossier_marker})

        # filter the brain of self.context
        context_path = '/'.join(self.context.getPhysicalPath())
        brains = filter(lambda brain: brain.getPath() != context_path,
                        brains)

        # any results?
        if len(brains) == 0:
            return ''

        info = getUtility(IContactInformation)

        # create rows in latex
        for brain in brains:

            rows.append(self._prepare_table_row(
                    str(brain.sequence_number),
                    getattr(brain, 'filing_no', None) or '',
                    str(brain.Title),
                    info.describe(brain.responsible),
                    self.context.translate(brain.review_state,
                                           domain='plone'),
                    readable_date(brain, brain.start),
                    ))

        return self.subdossiers(rows=''.join(rows))
