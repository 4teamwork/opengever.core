from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.dossier.filing.form import FILING_NO_KEY
from opengever.dossier.filing.form import IFilingFormSchema
from opengever.dossier.filing.form import METHOD_FILING
from opengever.dossier.filing.form import METHOD_RESOLVING
from opengever.dossier.filing.form import METHOD_RESOLVING_AND_FILING
from opengever.dossier.filing.form import METHOD_RESOLVING_EXISTING_FILING
from opengever.dossier.interfaces import IDossierArchiver
from opengever.dossier.resolve import get_resolver
from opengever.dossier.resolve import InvalidDates
from opengever.dossier.resolve import PreconditionsViolated
from opengever.dossier.statusmessage_mixin import DossierResolutionStatusmessageMixin
from opengever.ogds.base.utils import get_current_admin_unit
from persistent.dict import PersistentDict
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Transience.Transience import Increaser
from z3c.form import button
from z3c.form import field
from z3c.form.browser import radio
from z3c.form.form import Form
from z3c.form.interfaces import INPUT_MODE
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.schema.vocabulary import getVocabularyRegistry


class ArchiveForm(Form, DossierResolutionStatusmessageMixin):

    label = _(u'heading_archive_form', u'Archive Dossier')
    fields = field.Fields(IFilingFormSchema)
    ignoreContext = True

    # define custom widgets.
    fields['filing_action'].widgetFactory[INPUT_MODE] = radio.RadioFieldWidget
    fields['dossier_enddate'].widgetFactory[INPUT_MODE] = DatePickerFieldWidget

    @button.buttonAndHandler(_(u'button_archive', default=u'Archive'))
    def archive(self, action):
        """Try to archive this dossier.

        For that to happen, first all subdossiers need to have filing_no
        and end_date set, and then be resolved. If resolving any of the
        subdossier fails, we'll throw and error and return.
        """

        data, errors = self.extractData()

        # Abort if there were errors
        if len(errors) > 0:
            return
        self.ptool = getToolByName(self.context, 'plone_utils')
        self.wft = self.context.portal_workflow

        action = data.get('filing_action')
        filing_year = data.get('filing_year')
        filing_no = None
        filing_prefix = data.get('filing_prefix')
        end_date = data.get('dossier_enddate')

        if action == METHOD_FILING:
            # allready resolved only give a filing number
            IDossierArchiver(self.context).archive(filing_prefix, filing_year)
            self.ptool.addPortalMessage(
                _("The filing number has been given."), type="info")
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        # Validate resolving preconditions
        resolver = get_resolver(self.context)
        try:
            resolver.raise_on_failed_preconditions()

        except PreconditionsViolated as exc:
            return self.show_errors(exc.errors)

        except InvalidDates as exc:
            return self.show_invalid_end_dates(titles=exc.invalid_dossier_titles)

        IDossierArchiver(self.context).run(
            filing_action=action, filing_prefix=filing_prefix,
            filing_year=filing_year)

        # If everything went well, resolve the main dossier
        resolver.resolve(end_date=end_date, **data)

        self.ptool.addPortalMessage(
            _("The Dossier has been resolved"), type="info")
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


@implementer(IDossierArchiver)
@adapter(IDossierMarker)
class Archiver(object):

    def __init__(self, context):
        self.context = context

    def run(self, **kwargs):

        action = kwargs['filing_action']
        filing_year = kwargs['filing_year']
        filing_prefix = kwargs['filing_prefix']

        if action == METHOD_RESOLVING_AND_FILING:
            self.archive(filing_prefix, filing_year)

        elif action == METHOD_RESOLVING_EXISTING_FILING:
            # archive all with the existing filing number
            filing_no = IFilingNumber(self.context).filing_no
            filing_prefix = IDossier(self.context).filing_prefix
            self.archive(filing_prefix, filing_year, number=filing_no)

        elif action == METHOD_RESOLVING:
            # only update the prefixes
            if filing_prefix:
                self.update_prefix(filing_prefix)

    def update_prefix(self, prefix):
        """Update the filing prefix on the dossier and
        recursively on all subdossiers.
        """
        self._recursive_update_prefix(self.context, prefix)

    def _recursive_update_prefix(self, dossier, prefix):
        IDossier(dossier).filing_prefix = prefix
        dossier.reindexObject(idxs=['filing_no', 'searchable_filing_no', 'SearchableText'])
        for subdossier in dossier.get_subdossiers(depth=1):
            self._recursive_update_prefix(subdossier.getObject(), prefix)

    def archive(self, prefix, year, number=None):
        """Generate a correct filing number and
        set it recursively on every subdossier."""

        if not number:
            number = self.generate_number(prefix, year)
        self._recursive_archive(self.context, number, prefix)

    def _recursive_archive(self, dossier, number, prefix):

        IFilingNumber(dossier).filing_no = number

        IDossier(self.context).filing_prefix = prefix
        dossier.reindexObject(idxs=['filing_no', 'searchable_filing_no', 'SearchableText'])

        for i, subdossier in enumerate(dossier.get_subdossiers(depth=1),
                                       start=1):
            self._recursive_archive(
                subdossier.getObject(), '%s.%i' % (number, i), prefix)

    def generate_number(self, prefix, year):
        """Generate the complete filing number and
        set the number and prefix on the dossier."""

        prefix_title = self._get_term_title(prefix,
            'opengever.dossier.type_prefixes')

        # key
        key = '%s-%s' % (prefix_title, year)
        # assemble filing_no
        filing_no = '%s-%s-%s-%s' % (self._get_admin_unit_title(), prefix_title,
            year, self._get_sequence(key))

        return filing_no

    def get_indexer_value(self, searchable=False):
        """Return the filing value for the filing_no indexer.
        For Dossiers without a number and only a prefix it return the half
        of the number."""

        value = None
        if IFilingNumber(self.context).filing_no:
            value = IFilingNumber(self.context).filing_no

        elif IDossier(self.context).filing_prefix:
            value = '%s-%s-?' % (
                self._get_admin_unit_title(),
                self._get_term_title(
                    IDossier(self.context).filing_prefix,
                    'opengever.dossier.type_prefixes'),
                )
            if searchable:
                # cut the -? away
                value = value[:-2]

        if value:
            if searchable:
                return value.replace('-', ' ')
            return value
        return

    def _get_term_title(self, prefix, vocabulary):
        """ Get the value and not the key from the prefix vocabulary.
        """
        return getVocabularyRegistry().get(self.context,
            vocabulary).by_token.get(prefix).title

    def _get_sequence(self, key):
        """compute the filing sequence"""

        portal = getUtility(ISiteRoot)
        ann = IAnnotations(portal)

        if FILING_NO_KEY not in ann.keys():
            ann[FILING_NO_KEY] = PersistentDict()

        mappping = ann.get(FILING_NO_KEY)
        if key not in mappping:
            mappping[key] = Increaser(0)

        inc = mappping[key]
        inc.set(inc() + 1)
        mappping[key] = inc
        return str(inc())

    def _get_admin_unit_title(self):
        return get_current_admin_unit().label()
