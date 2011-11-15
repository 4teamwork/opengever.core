from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.table import helper
from opengever.base.interfaces import ISequenceNumber
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.latex.layouts.zug_landscape import ZugLandscapeLayout
from opengever.latex.template import LatexTemplateFile
from opengever.latex.views.baselisting import BasePDFListing
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_client
from zope.component import getUtility


class TasksListingPDF(BasePDFListing):
    """Create a PDF listing of all tasks, which were selected in a tabbed view.
    """

    template = LatexTemplateFile('taskslisting_content.tex')

    def get_layout(self):
        """Returns the layout to use.
        """
        return ZugLandscapeLayout(show_organisation=True)

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
            dossier_seq_num, dossier_title = self.get_dossier_sequence_number_and_title(
                item)

            data.append(self._prepare_table_row(
                    unicode(item.sequence_number).encode('utf-8'),
                    helper.readable_date(item, item.deadline),
                    unicode(getattr(item, 'Title',getattr(item, 'title', ''))
                            ).encode('utf-8'),
                    '%s / %s' % (client.title,
                                 info.describe(item.issuer)),
                    dossier_seq_num,
                    dossier_title,
                    unicode(getattr(item, 'reference',
                                getattr(item, 'reference_number', ''))
                            ).encode('utf-8'),
                    ))

        return ''.join(data)

    def get_dossier_sequence_number_and_title(self, item):
        """Returns the sequence number and title of the parent dossier of the item.
        `item` may be a brain or a sqlalchemy task object.
        """

        try:
            # brain?
            item.getPath()
        except AttributeError:
            is_brain = False
        else:
            is_brain = True

        if is_brain:
            dossier = item.getObject()

            while not IDossierMarker.providedBy(dossier):
                if IPloneSiteRoot.providedBy(dossier):
                    return ('', '')
                dossier = aq_parent(aq_inner(dossier))

            sequence_number = getUtility(ISequenceNumber).get_number(dossier)
            title = dossier.Title()

        else:
            # sqlalchemy task object
            sequence_number = item.dossier_sequence_number
            title = item.breadcrumb_title.split(' > ')[-2]

        if isinstance(title, unicode):
            title = title.encode('utf-8')

        return str(sequence_number), title
