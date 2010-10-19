from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.dossier.behaviors.dossier import IDossier
from opengever.latex.template import LatexTemplateFile
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_client
from opengever.repository.interfaces import IRepositoryFolder
from opengever.latex.views.baselisting import BasePDFListing
from zope.component import getUtility


class DossierListingPDF(BasePDFListing):
    """Listing of all dossiers as PDF (recursive). Is called from
    a tabbed view or folder_contents and expects "paths" to be in
    the request.
    """

    template = LatexTemplateFile('dossierlisting_content.tex')

    def render(self):
        return self.template(rows=self.get_listing_rows())

    def get_listing_rows(self):
        """Returns the listing rows rendered in latex.
        """
        data = []

        sequence_number = getUtility(ISequenceNumber)
        client = get_current_client()
        info = getUtility(IContactInformation)

        for brain in self.get_selected_brains():
            obj = brain.getObject()
            dossier = IDossier(obj)
            ref = IReferenceNumber(obj)
            obj_state = obj.restrictedTraverse('@@plone_context_state')

            # walk the breadcrumbs up and search for a repository folder
            repository_folder = obj
            while not IRepositoryFolder.providedBy(repository_folder):
                repository_folder = aq_parent(aq_inner(repository_folder))
                if IPloneSiteRoot.providedBy(repository_folder):
                    repository_folder = None
                    break

            # readable responsible
            responsible = '%s / %s' % (
                client.title,
                info.describe(dossier.responsible))

            # calculate start
            if dossier.start:
                start = dossier.start.strftime('%d.%m.%Y')

            # html 2 latex
            data.append(' & '.join((
                        str(sequence_number.get_number(obj)),
                        ref.get_number(),
                        repository_folder and repository_folder.Title() or '',
                        obj.Title(),
                        responsible,
                        self.context.translate(obj_state.workflow_state(),
                                               domain='plone'),
                        start,
                        )))

        if len(data):
            # we want a \\ and \hline after EVERY line, so lets add a empty
            # entry
            data.append('')

        return '\\\\ \\hline\n'.join(data)


