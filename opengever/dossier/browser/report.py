from five import grok
from opengever.base.reporter import format_datetime, get_date_style
from opengever.base.reporter import readable_author
from opengever.base.reporter import StringTranslater, XLSReporter
from opengever.dossier import _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage


class DossierReporter(grok.View):
    """View that generate an excel spreadsheet with the XLSReporter,
    which list all dossier and their important attributes.
    """

    grok.context(IPloneSiteRoot)
    grok.name('dossier_report')
    grok.require('zope2.View')

    def render(self):

        dossier_attributes = [
            {'id':'Title', 'title':_('label_title')},
            {'id':'start', 'title':_('label_start'),
             'transform':format_datetime, 'style':get_date_style()},
            {'id':'end', 'title':_('label_end'),
             'transform':format_datetime, 'style':get_date_style()},
            {'id':'responsible', 'title':_('label_responsible'),
             'transform':readable_author},
            {'id':'filing_no', 'title':_('filing_no')},
            {'id':'review_state', 'title':_('review_state'),
             'transform':StringTranslater(
                self.context.REQUEST, 'plone').translate},
            {'id':'reference', 'title':_('label_reference_number')},
        ]


        dossiers = self.context.portal_catalog(
            object_provides = \
                'opengever.dossier.behaviors.dossier.IDossierMarker',
            is_subdossier=False)

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
