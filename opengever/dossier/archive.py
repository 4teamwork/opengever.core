from collective.elephantvocabulary import wrap_vocabulary
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.dossier.interfaces import IDossierArchiver
from opengever.dossier.resolve import DossierResolutionStatusmessageMixin
from opengever.dossier.resolve import get_resolver
from opengever.dossier.resolve import InvalidDates
from opengever.dossier.resolve import PreconditionsViolated
from opengever.ogds.base.utils import get_current_admin_unit
from persistent.dict import PersistentDict
from plone.supermodel import model
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Transience.Transience import Increaser
from z3c.form import button, field
from z3c.form import validator
from z3c.form.browser import radio
from z3c.form.form import Form
from z3c.form.interfaces import INPUT_MODE
from ZODB.POSException import ConflictError
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import getVocabularyRegistry
from zope.schema.vocabulary import SimpleVocabulary
import re


# action vocabulary terms
RESOLVE_AND_NUMBER = _('resolve and set filing no')
ONLY_RESOLVE = _('only resolve, set filing no later')
RESOLVE_WITH_EXISTING_NUMBER = _('resolve and take the existing filing no')
RESOLVE_WITH_NEW_NUMBER = _('resolve and set a new filing no')
ONLY_NUMBER = _('set a filing no')

# filing methods
METHOD_RESOLVING_AND_FILING = 0
METHOD_RESOLVING = 1
METHOD_FILING = 2
METHOD_RESOLVING_EXISTING_FILING = 3

# annotation key
FILING_NO_KEY = "filing_no"

# filing no pattern
FILLING_NO_PATTERN = r'(.*)-(.*)-([0-9]*)-([0-9]*)'


class MissingValue(Invalid):
    """ The Missing value was defined Exception."""
    __doc__ = _(u"Not all required fields are filled.")


class EnddateValidator(validator.SimpleFieldValidator):
    """check if the subdossier hasn't a younger date,
    than the given enddate"""

    def validate(self, value):
        if not value:
            raise MissingValue(
                _(u'error_enddate', default=u'The enddate is required.'))

        earliest_date = self.context.earliest_possible_end_date()
        if earliest_date and value < earliest_date:
            raise Invalid(
                _(u'The given end date is not valid, it needs to be younger or\
                  equal than ${date} (the youngest contained object).',
                  mapping=dict(date=earliest_date.strftime('%d.%m.%Y'),),))


def tryint(i):
    try:
        int(i)
        return True
    except ConflictError:
        raise
    except Exception:
        return False


def valid_filing_year(value):
    if tryint(value):
        if 1900 < int(value) < 3000:
            if str(int(value)) == value:
                return True
    raise Invalid(_(u'The given value is not a valid Year.'))


@provider(IContextSourceBinder)
def get_filing_actions(context):
    """Create a vocabulary with different actions,
    depending on the actual review_state."""

    wft = getToolByName(context, 'portal_workflow')
    review_state = wft.getInfoFor(context, 'review_state', None)
    filing_no = IFilingNumber(context).filing_no

    values = []

    if review_state != 'dossier-state-resolved':

        # not archived yet or not a valid filing_no
        if filing_no and re.search(FILLING_NO_PATTERN, filing_no):
            values.append(SimpleVocabulary.createTerm(
                    METHOD_RESOLVING_EXISTING_FILING,
                    RESOLVE_WITH_EXISTING_NUMBER,
                    RESOLVE_WITH_EXISTING_NUMBER))

            values.append(SimpleVocabulary.createTerm(
                    METHOD_RESOLVING_AND_FILING,
                    RESOLVE_WITH_NEW_NUMBER,
                    RESOLVE_WITH_NEW_NUMBER))

        # already archived
        else:
            values.append(SimpleVocabulary.createTerm(
                    METHOD_RESOLVING_AND_FILING,
                    RESOLVE_AND_NUMBER, RESOLVE_AND_NUMBER))

            values.append(SimpleVocabulary.createTerm(
                    METHOD_RESOLVING, ONLY_RESOLVE, ONLY_RESOLVE))
    # already resolved
    else:
        if not filing_no:
            values.append(SimpleVocabulary.createTerm(
                    METHOD_FILING, ONLY_NUMBER, ONLY_NUMBER))

    return SimpleVocabulary(values)


@provider(IContextAwareDefaultFactory)
def filing_prefix_default(context):
    """If the dossier already has a filing_prefix set, use that one as the
    default for the filing_prefix in the ArchiveForm.

    context: Dossier that's being archived.
    """
    prefix = IDossier(context).filing_prefix
    if prefix:
        return prefix.decode('utf-8')
    # Need to return None here instead of empty string, because otherwise
    # validation in zope.schema's DefaultProperty fails (value not in vocab)
    return None


@provider(IContextAwareDefaultFactory)
def filing_year_default(context):
    """Propose default for filing_year based on the most recent date of
    any object contained in the dossier or the dossier itself.

    context: Dossier that's being archived.
    """
    youngest_date = context.earliest_possible_end_date()
    if youngest_date:
        # filing_year is of type TextLine for some reason
        return unicode(youngest_date.year)
    return None


@provider(IContextAwareDefaultFactory)
def dossier_enddate_default(context):
    """Suggested default for the dossier's enddate.

    context: Dossier that's being archived.
    """
    if IDossier(context).end and context.has_valid_enddate():
        return IDossier(context).end
    return context.earliest_possible_end_date()


class IArchiveFormSchema(model.Schema):

    filing_prefix = schema.Choice(
        title=_(u'filing_prefix', default="filing prefix"),
        source=wrap_vocabulary(
            'opengever.dossier.type_prefixes',
            visible_terms_from_registry="opengever.dossier"
            '.interfaces.IDossierContainerTypes.type_prefixes'),
        required=False,
        defaultFactory=filing_prefix_default,
    )

    dossier_enddate = schema.Date(
        title=_(u'label_end', default=u'Closing Date'),
        required=True,
        defaultFactory=dossier_enddate_default,
    )

    filing_year = schema.TextLine(
        title=_(u'filing_year', default="filing Year"),
        constraint=valid_filing_year,
        required=False,
        defaultFactory=filing_year_default,
    )

    filing_action = schema.Choice(
        title=_(u'filing_action', default="Action"),
        source=get_filing_actions,
        required=True,
    )

    @invariant
    def validate_field_requirement(data):
        # validat if all required fields, depends on the selectied action
        # are filled
        if data.filing_action in [METHOD_RESOLVING_AND_FILING,
                                  METHOD_FILING]:
            if not data.filing_prefix or not data.filing_year:
                raise Invalid(
                    _(u"When the Action give filing number is selected, \
                        all fields are required."))


class ArchiveForm(Form, DossierResolutionStatusmessageMixin):

    label = _(u'heading_archive_form', u'Archive Dossier')
    fields = field.Fields(IArchiveFormSchema)
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

        if action == METHOD_RESOLVING_AND_FILING:
            IDossierArchiver(self.context).archive(filing_prefix, filing_year)

        if action == METHOD_RESOLVING_EXISTING_FILING:
            # archive all with the existing filing number
            filing_no = IFilingNumber(self.context).filing_no
            filing_prefix = IDossier(self.context).filing_prefix
            IDossierArchiver(self.context).archive(
                filing_prefix, filing_year, number=filing_no)

        if action == METHOD_RESOLVING:
            # only update the prefixes
            if filing_prefix:
                IDossierArchiver(self.context).update_prefix(filing_prefix)

        # If everything went well, resolve the main dossier
        resolver.resolve(end_date=end_date)

        self.ptool.addPortalMessage(
            _("The Dossier has been resolved"), type="info")
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


validator.WidgetValidatorDiscriminators(
    EnddateValidator,
    field=IArchiveFormSchema['dossier_enddate'],
)


@implementer(IDossierArchiver)
@adapter(IDossierMarker)
class Archiver(object):

    def __init__(self, context):
        self.context = context

    def update_prefix(self, prefix):
        """Update the filing prefix on the dossier and
        recursively on all subdossiers.
        """
        self._recursive_update_prefix(self.context, prefix)

    def _recursive_update_prefix(self, dossier, prefix):
        IDossier(dossier).filing_prefix = prefix
        dossier.reindexObject(idxs=['filing_no', 'searchable_filing_no'])
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
        dossier.reindexObject(idxs=['filing_no', 'searchable_filing_no'])

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
