from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.latex.template import LatexTemplateFile
from opengever.ogds.base.utils import get_current_client
from opengever.repository.interfaces import IRepositoryFolder
from opengever.latex.views.baselisting import BasePDFListing
from zope.component import getUtility


class TasksListingPDF(BasePDFListing):
    """Create a PDF listing of all tasks, which were selected in a tabbed view.
    """

    template = LatexTemplateFile('taskslisting_content.tex')

    def render(self):
        return self.template(rows=self.get_listing_rows())

    def get_listing_rows(self):
        """Returns the listing rows rendered in latex.
        """
        data = []

        sequence_number = getUtility(ISequenceNumber)
        client = get_current_client()

        for brain in self.get_selected_brains():
            obj = brain.getObject()
            ref = IReferenceNumber(obj)

            # walk the breadcrumbs up and search for a repository folder
            dossier = obj
            while not IRepositoryFolder.providedBy(dossier):
                dossier = aq_parent(aq_inner(dossier))
                if IPloneSiteRoot.providedBy(dossier):
                    dossier = None
                    break

            # calculate start
            if obj.deadline:
                deadline = obj.deadline.strftime('%d.%m.%Y')

            # html 2 latex
            data.append(' & '.join((
                        str(sequence_number.get_number(obj)),
                        deadline,
                        obj.Title(),
                        client.title,
                        str(sequence_number.get_number(dossier)),
                        ref.get_number())))

        if len(data):
            # we want a \\ and \hline after EVERY line, so lets add a empty
            # entry
            data.append('')

        return '\\\\ \\hline\n'.join(data)
