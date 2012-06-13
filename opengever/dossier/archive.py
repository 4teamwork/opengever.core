from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Transience.Transience import Increaser
from collective.elephantvocabulary import wrap_vocabulary
from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base.interfaces import IBaseClientID
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.interfaces import IDossierArchiver
from opengever.dossier.interfaces import IDossierResolver
from persistent.dict import PersistentDict
from plone.directives import form as directives_form
from plone.registry.interfaces import IRegistry
from z3c.form import button, field
from z3c.form import validator
from z3c.form.browser import radio
from z3c.form.interfaces import INPUT_MODE
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility, provideAdapter
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, getVocabularyRegistry


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

# annotation key
FILING_NO_KEY = "filing_no"


class MissingValue(Invalid):
    """ The Missing value was defined Exception."""
    __doc__ = _(u"Not all required fields are filled")


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


@grok.provider(IContextSourceBinder)
def get_filing_actions(context):
    """Create a vocabulary with different actions,
    depending on the actual review_state."""

    wft = getToolByName(context, 'portal_workflow')
    review_state = wft.getInfoFor(context, 'review_state', None)
    filing_no = IDossier(context).filing_no

    values = []
    if review_state != 'dossier-state-resolved':
        # not archived yet
        if not filing_no:
            values.append(SimpleVocabulary.createTerm(
                    METHOD_RESOLVING_AND_FILING,
                    RESOLVE_AND_NUMBER, RESOLVE_AND_NUMBER))

            values.append(SimpleVocabulary.createTerm(
                    METHOD_RESOLVING, ONLY_RESOLVE, ONLY_RESOLVE))

        # allready archived
        else:
            values.append(SimpleVocabulary.createTerm(
                    METHOD_RESOLVING,
                    RESOLVE_WITH_EXISTING_NUMBER,
                    RESOLVE_WITH_EXISTING_NUMBER))

            values.append(SimpleVocabulary.createTerm(
                    METHOD_RESOLVING_AND_FILING,
                    RESOLVE_WITH_NEW_NUMBER,
                    RESOLVE_WITH_NEW_NUMBER))
    # allready resolved
    else:
        if not filing_no:
            values.append(SimpleVocabulary.createTerm(
                    METHOD_FILING, ONLY_NUMBER, ONLY_NUMBER))

    return SimpleVocabulary(values)


class IArchiveFormSchema(directives_form.Schema):

    filing_prefix = schema.Choice(
        title=_(u'filing_prefix', default="filing prefix"),
        source=wrap_vocabulary(
            'opengever.dossier.type_prefixes',
            visible_terms_from_registry="opengever.dossier.interfaces.\
                IDossierContainerTypes.type_prefixes"),
        required=False,
    )

    dossier_enddate = schema.Date(
        title=_(u'label_end', default=u'Closing Date'),
        description=_(u'help_end', default=u''),
        required=True,
    )

    filing_year = schema.TextLine(
        title=_(u'filing_year', default="filing Year"),
        required=False,
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


# defaults
@directives_form.default_value(field=IArchiveFormSchema['filing_prefix'])
def filing_prefix_default_value(data):
    """If allready a filing_prefix is selected on the dossier,
    it return this as default."""

    prefix = IDossier(data.context).filing_prefix
    if prefix:
        return prefix.decode('utf-8')
    return ""


@directives_form.default_value(field=IArchiveFormSchema['filing_year'])
def filing_year_default_value(data):
    last_date = data.context.earliest_possible_end_date()
    if last_date:
        return str(last_date.year)
    return None


@directives_form.default_value(field=IArchiveFormSchema['dossier_enddate'])
def default_end_date(data):
    if IDossier(data.context).end and data.context.has_valid_enddate():
        return IDossier(data.context).end
    return data.context.earliest_possible_end_date()


class ArchiveForm(directives_form.Form):
    grok.context(IDossierMarker)
    grok.name('transition-archive')
    grok.require('zope2.View')

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

        # archiving must passed to the resolving view
        resolver = IDossierResolver(self.context)
        if resolver.is_resolve_possible():
            raise TypeError
        if resolver.are_enddates_valid():
            raise TypeError

        if action == METHOD_RESOLVING_AND_FILING:
            IDossierArchiver(self.context).archive(filing_prefix, filing_year)

        if action == METHOD_RESOLVING:
            # archive all with the existing filing number
            filing_no = IDossier(self.context).filing_no
            IDossierArchiver(self.context).archive(
                filing_prefix, filing_year, number=filing_no)

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

provideAdapter(EnddateValidator)


class Archiver(grok.Adapter):

    grok.context(IDossierMarker)
    grok.implements(IDossierArchiver)

    def archive(self, prefix, year, number=None):
        """Generate a correct filing number and
        set it recursively on every subdossier."""

        if not number:
            number = self.generate_number(prefix, year)
        self._recursive_archive(self.context, number, prefix)

    def _recursive_archive(self, dossier, number, prefix):

        IDossier(dossier).filing_no = number
        IDossier(self.context).filing_prefix = prefix
        dossier.reindexObject(idxs=['filing_no', 'searchable_filing_no'])

        for i, subdossier in enumerate(dossier.get_subdossiers(), start=1):
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
        filing_no = '%s-%s-%s-%s' % (self._get_client_id(), prefix_title,
            year, self._get_sequence(key))

        return filing_no

    def get_indexer_value(self, searchable=False):
        """Return the filing value for the filing_no indexer.
        For Dossiers without a number and only a prefix it return the half
        of the number."""

        dossier = IDossier(self.context)
        value = None
        if dossier.filing_no:
            value = dossier.filing_no

        elif dossier.filing_prefix:
            value = '%s-%s-?' % (
                self._get_client_id(),
                self._get_term_title(
                    dossier.filing_prefix,
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

    def _get_client_id(self):
        """"compute filing_client from the registry."""

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IBaseClientID)
        return getattr(proxy, 'client_id')
