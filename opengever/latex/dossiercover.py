from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from five import grok
from ftw.pdfgenerator.browser.standalone import BaseStandalonePDFView
from opengever.base.interfaces import IBaseClientID
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
from opengever.ogds.base.interfaces import IContactInformation
from opengever.repository.interfaces import IRepositoryFolder
from plone.registry.interfaces import IRegistry
from zope.component import getUtility, getAdapter
from zope.schema import vocabulary


class DossierCoverPDFView(grok.View, BaseStandalonePDFView):
    grok.context(IDossierMarker)
    grok.name('dossier_cover_pdf')
    grok.require('zope2.View')

    template_directories = ['templates']
    template_name = 'dossiercover.tex'

    __call__ = BaseStandalonePDFView.__call__

    def __init__(self, context, request):
        BaseStandalonePDFView.__init__(self, context, request)
        grok.View.__init__(self, context, request)

    def render(self):
        # grok.View.render --> use __call__ instead
        # MakoLaTeXView --> render layout instead
        return ''

    def before_render_hook(self):
        self.use_package('ae,aecompl')
        self.use_package('babel', options='ngerman', append_options=False)
        self.use_package('fontenc', options='T1', append_options=False)

        self.use_package('geometry', options='left=5cm')
        self.use_package('geometry', options='right=5cm')
        self.use_package('geometry', options='top=15cm')
        self.use_package('geometry', options='bottom=3cm')

        self.use_package('graphicx')
        self.use_package('inputenc', options='utf8', append_options=False)
        self.use_package('textcomp')
        self.use_package('tabularx')

        self.add_raw_template_file('line.png')

    def get_render_arguments(self):
        return {
            'clientid': self.convert_plain(self.get_clientid()),
            'repository': self.convert_plain(self.get_reversed_breadcrumbs()),
            'referencenr': self.convert_plain(self.get_referencenumber()),
            'filingprefix': self.convert_plain(self.get_filingprefix()),
            'filingnr': self.convert_plain(
                IDossier(self.context).filing_no or ''),

            'sequencenr': self.convert_plain(
                str(getUtility(ISequenceNumber).get_number(self.context))),

            'title': self.convert_plain(self.context.Title()),
            'description': self.convert(self.get_description()),
            'responsible': self.convert_plain(self.get_responsible()),

            'start': self.convert_plain(self.context.toLocalizedTime(
                    str(IDossier(self.context).start)) or '-'),
            'end': self.convert_plain(self.context.toLocalizedTime(
                    str(IDossier(self.context).end)) or '-'),

            'parentDossierTitle': self.convert_plain(
                self.get_parent_dossier_title())
            }

    def get_description(self):
        return self.context.Description().replace('\n', '<br />')

    def get_parent_dossier_title(self):
        obj = aq_parent(aq_inner(self.context))

        while not IPloneSiteRoot.providedBy(obj):
            if IDossierMarker.providedBy(obj):
                return obj.Title()
            else:
                obj = aq_parent(aq_inner(obj))

        return ''

    def get_reversed_breadcrumbs(self):
        obj = self.context
        titles = []

        while not IPloneSiteRoot.providedBy(obj):
            if IRepositoryFolder.providedBy(obj):
                titles.append(obj.Title())

            obj = aq_parent(aq_inner(obj))

        return ' / '.join(titles)

    def get_clientid(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IBaseClientID)
        return proxy.client_id

    def get_referencenumber(self):
        return getAdapter(self.context, IReferenceNumber).get_number()

    def get_filingprefix(self):
        value = IDossier(self.context).filing_prefix

        if value:
            # Get the value and not the key from the prefix vocabulary
            voc = vocabulary.getVocabularyRegistry().get(
                self.context, 'opengever.dossier.type_prefixes')

            return voc.by_token.get(value).title

        else:
            return ''

    def get_responsible(self):
        info = getUtility(IContactInformation)
        value = IDossier(self.context).responsible
        return info.describe(value)
