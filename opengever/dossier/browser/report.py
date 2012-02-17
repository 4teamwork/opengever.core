from five import grok
from opengever.base.reporter import format_datetime, get_date_style
from opengever.base.reporter import readable_author
from opengever.base.reporter import StringTranslater, XLSReporter
from opengever.dossier import _
from zope.interface import Interface
from Products.statusmessages.interfaces import IStatusMessage


class DossierReporter(grok.View):
    """View that generate an excel spreadsheet with the XLSReporter,
    which list the selected dossier (paths in request)
    and their important attributes.
    """

    grok.context(Interface)
    grok.name('dossier_report')
    grok.require('zope2.View')

    def render(self):

        if not self.request.get('paths'):
            msg = _(
                u'error_no_items', default=u'You have not selected any Items')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return_temp = self.request.get('orig_template', self.context.absolute_url())
            return self.request.RESPONSE.redirect(return_temp)

        # get the given dossiers
        portal_catalog = self.context.portal_catalog
        dossiers = []
        for path in self.request.get('paths'):
            dossiers.append(
                portal_catalog(path={'query': path, 'depth': 0})[0]
                )

        # attributes mapping
        dossier_attributes = [
            {'id':'Title', 'title':_('label_title')},
            {'id':'start', 'title':_('label_start'),
             'transform':format_datetime, 'style':get_date_style()},
            {'id':'end', 'title':_('label_end'),
             'transform':format_datetime, 'style':get_date_style()},
            {'id':'responsible', 'title':_('label_responsible'),
             'transform':readable_author},
            {'id':'filing_no', 'title':_('filing_no')},
            {'id':'review_state',
             'title':_('label_review_state', default='Review state'),
             'transform':StringTranslater(
                self.context.REQUEST, 'plone').translate},
            {'id':'reference', 'title':_('label_reference_number')},
        ]

        # generate the xls data with the XLSReporter
        reporter = XLSReporter(
            self.context.REQUEST, dossier_attributes, dossiers)

        data = reporter()
        if not data:
            msg = _(u'Could not generate the report')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        response = self.request.RESPONSE

        response.setHeader('Content-Type', 'application/vnd.ms-excel')
        response.setHeader('Content-Disposition',
                           'attachment;filename="dossier_report.xls"')
        return data
