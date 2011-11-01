from Products.CMFCore.utils import getToolByName
from opengever.latex.template import LatexTemplateFile
from opengever.latex.views.baselisting import BasePDFListing
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_client
from ftw.table import helper
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

        # item may be brain or sqlalchemy task representation (globalindex)
        for item in self.get_selected_data():
            data.append(self._prepare_table_row(
                    unicode(item.sequence_number).encode('utf-8'),
                    helper.readable_date(item, item.deadline),
                    unicode(getattr(item, 'Title',getattr(item, 'title', ''))
                            ).encode('utf-8'),
                    '%s / %s' % (client.title,
                                 info.describe(item.issuer)),
                    unicode(self.get_dossier_sequence_number(item)
                            ).encode('utf-8'),
                    unicode(getattr(item, 'reference',
                                getattr(item, 'reference_number', ''))
                            ).encode('utf-8'),
                    ))

        return ''.join(data)

    def get_dossier_sequence_number(self, item):
        """Searches the first parental dossier relative to the task
        (breadcrumbs like) and returns its sequence number.

        A item my be the brain of the task or the sqlalchemy task
        representation.
        """

        dossier_marker = 'opengever.dossier.behaviors.dossier.IDossierMarker'

        try:
            # brain?
            path = item.getPath()
        except AttributeError:
            # sqlalchemy ! -> the information is stored on the item already
            return item.dossier_sequence_number
        else:
            path = path.split('/')[:-1]

        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        portal_path = '/'.join(portal.getPhysicalPath())
        catalog = getToolByName(self.context, 'portal_catalog')

        while path and '/'.join(path) != portal_path:
            brains = catalog({'path': {'query': '/'.join(path),
                                       'depth': 0},
                              'object_provides': dossier_marker})

            if len(brains):
                return brains[0].sequence_number
            else:
                path = path[:-1]

        return ''
