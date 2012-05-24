from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.base.reporter import StringTranslater, XLSReporter
from opengever.base.reporter import format_datetime, get_date_style
from opengever.base.reporter import readable_author
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.dossier import _
from zope.interface import Interface


def _get_filing_part(filing_number, part):
    if filing_number:
        parts = filing_number.split('-')
        if len(parts) == 4:
            try:
                return int(parts[part])
            except ValueError:
                return parts[part]
        return


def filing_no_year(filing_number):
    """Helper wich only return the year of the filing number"""

    return _get_filing_part(filing_number, 2)


def filing_no_number(filing_number):
    """Helper wich only return the number of the filing number"""

    return _get_filing_part(filing_number, 3)


class DossierReporter(grok.View):
    """View that generate an excel spreadsheet with the XLSReporter,
    which list the selected dossier (paths in request)
    and their important attributes.
    """

    grok.context(Interface)
    grok.name('dossier_report')
    grok.require('zope2.View')

    def get_selected_dossiers(self):

        # get the given dossiers
        catalog = getToolByName(self.context, 'portal_catalog')
        dossiers = []
        for path in self.request.get('paths'):
            dossiers.append(
                catalog(path={'query': path, 'depth': 0})[0]
                )
        return dossiers

    def render(self):

        if not self.request.get('paths'):
            msg = _(
                u'error_no_items', default=u'You have not selected any Items')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return_temp = self.request.get(
                'orig_template', self.context.absolute_url())

            return self.request.RESPONSE.redirect(return_temp)

        dossiers = self.get_selected_dossiers()

        # attributes mapping
        dossier_attributes = [
            {'id':'Title',
             'title':_('label_title', default=u'title')},
            {'id':'start',
             'title':_(u'label_start', default=u'Opening Date'),
             'transform':format_datetime,
             'style':get_date_style()},
            {'id':'end',
             'title':_(u'label_end', default=u'Closing Date'),
             'transform':format_datetime,
             'style':get_date_style()},
            {'id':'responsible',
             'title':_(u'label_responsible', default='Responsible'),
             'transform':readable_author},
            {'id':'filing_no',
             'title':_(u'filing_no', default="Filing number")},
            {'id':'filing_no',
             'title':_('filing_no_year'),
             'transform': filing_no_year},
            {'id':'filing_no',
             'title':_('filing_no_number'),
             'transform': filing_no_number},
            {'id':'review_state',
             'title':_('label_review_state', default='Review state'),
             'transform':StringTranslater(
                self.request, 'plone').translate},
            {'id':'reference',
             'title':_(u'label_reference_number',
                       default=u'Reference Number')},
        ]

        # generate the xls data with the XLSReporter
        reporter = XLSReporter(
            self.request, dossier_attributes, dossiers)

        data = reporter()
        if not data:
            msg = _(u'Could not generate the report')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        response = self.request.RESPONSE

        response.setHeader('Content-Type', 'application/vnd.ms-excel')
        set_attachment_content_disposition(self.request, "dossier_report.xls")

        return data
