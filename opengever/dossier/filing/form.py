from opengever.base.vocabulary import wrap_vocabulary
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.filing import IFilingNumber
from plone.supermodel import model
from Products.CMFCore.utils import getToolByName
from z3c.form import validator
from ZODB.POSException import ConflictError
from zope import schema
from zope.interface import Invalid
from zope.interface import invariant
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import IContextSourceBinder
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


class IFilingFormSchema(model.Schema):

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


validator.WidgetValidatorDiscriminators(
    EnddateValidator,
    field=IFilingFormSchema['dossier_enddate'],
)
