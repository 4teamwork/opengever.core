from Products.CMFCore.utils import getToolByName
from ftw.table import helper
from opengever.latex.template import LatexTemplateFile
from opengever.latex.views.baselisting import BasePDFListing
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_client
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
        info = getUtility(IContactInformation)
        client = get_current_client()

        for brain in self.get_selected_brains():
            data.append(self._prepare_table_row(
                    str(brain.sequence_number),
                    helper.readable_date(brain, brain.deadline),
                    str(brain.Title),
                    '%s / %s' % (client.title,
                                 info.describe(brain.issuer)),
                    str(self.get_dossier_sequence_number(brain)),
                    str(brain.reference),
                    ))

        return ''.join(data)

    def get_dossier_sequence_number(self, brain):
        """Searches the first parental dossier relative to the `brain`
        (breadcrumbs like) and returns its sequence number.
        """

        dossier_marker = 'opengever.dossier.behaviors.dossier.IDossierMarker'

        path = brain.getPath().split('/')[:-1]
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        portal_path = '/'.join(portal.getPhysicalPath())
        catalog = getToolByName(self.context, 'portal_catalog')

        while path and '/'.join(path) != portal_path:
            brains = catalog({'path': {'query': '/'.join(path),
                                       'depth': 0},
                              'object_provides': dossier_marker})

            if len(brains):
                return brains[0].sequence_number

        return ''
