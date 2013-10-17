from Products.ZCatalog.interfaces import ICatalogBrain
from five import grok
from zope import schema
from zope.component import getAdapters
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class IOpengeverBaseLayer(Interface):
    """Marker interfaces for opengever base browserview customisations.
    """


class IOpengeverCatalogBrain(ICatalogBrain):
    """Detailed Interface for opengever CatalogBrain.
    Used for add an opengever specific CatalogContentlisting Adapter.
    """


class IBaseCustodyPeriods(Interface):
    custody_periods = schema.List(title=u"custody period",
                                  default=[u'0',
                                           u'30',
                                           u'100',
                                           u'150',
                                           ],
                                  value_type=schema.TextLine(),
                                  )


class IRetentionPeriodRegister(Interface):
    """ plone.registry register for retention_period
    """
    retention_period = schema.List(
        title=u'Retention period',
        description=u'Possible values for retention period in years.',
        default=[u'5',
                u'10',
                u'15',
                u'20',
                u'25'],
        value_type=schema.TextLine(),)


class IBaseClientID(Interface):
    client_id = schema.TextLine(
        title=u"Prefix of reference number",
        description=u'Enter the text which will be used as prefix\
            of the reference number of Opengever content.',
        default=u"OG")


class IReferenceNumberPrefix(Interface):
    """ The Reference Number Prefix Adapter Interface """


class IReferenceNumber(Interface):
    """ The reference number adapter is able to generate a full reference
    number including all parent reference-prefixes.
    Examples:

    GD 2.3 / 4.5 / 123
    * GD : client specific short name
    * 2 : reference_number prefix of first RepositoryFolder
    * 3 : reference_number prefix of second RepositoryFolder
    * / : Seperator between RFs and Dossiers
    * 4 : reference_number prefix of first dossier
    * 5 : reference_number prefix of second dossier
    * / : Seperator between Dossiers and Document
    * 123 : sequence_number of Document
    """

    def get_number():
        """ Returns the reference number of the context
        """

    def get_local_number():
        """Returns only the reference number part of the context."""

    def append_local_number(numbers):
        """Append the number part of the context in the specific list
        in the given numbers dict."""

    def get_parent_numbers():
        """Returns a dict with list of all number parts, from the context up to
        the plone site, grouped by the context type.

        Examples:
        {'site': ['OG'],
         'repository: ['3', '5' , '8']',
         'dossier: ['3', '3']'}
        """


class IReferenceNumberFormatter(Interface):

    def complete_number(numbers):
        """Generate the complete reference number, for the given numbers dict.
        """

    def repository_number(numbers):
        """Generate the reposiotry reference number part,
        for the given numbers dict.
        """

    def dossier_number(numbers):
        """Generate the dossier reference number part,
        for the given numbers dict.
        """


class ReferenceFormatterVocabulary(grok.GlobalUtility):
    """ Vocabulary of all users with a valid login.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.base.ReferenceFormatterVocabulary')

    def __call__(self, context):
        terms = []

        for name, formatter in getAdapters(
                [context, ], IReferenceNumberFormatter):
            terms.append(SimpleTerm(name))
        return SimpleVocabulary(terms)


class IReferenceNumberSettings(Interface):

    formatter = schema.Choice(
        title=u'Reference number formatter',
        description=u'Select one of the registered'
        'IReferenceNumberFormatter adapter',
        source='opengever.base.ReferenceFormatterVocabulary',
        default='dotted')

    refernce_prefix_starting_point = schema.TextLine(
        title=u"Starting Point for reference_number prefixs",
        description=u"Used as default when creating the first item on a level.",
        default=u"1")


class ISequenceNumber(Interface):
    """  The sequence number utility provides a getNumber(obj) method
    which returns a unique number for each object.
    """

    def get_number(self, obj):
        """ Returns the sequence number for the given *obj*
        """


class ISequenceNumberGenerator(Interface):
    """ The sequence number generator adapter generates a new sequence number
    for the adapted object
    """

    def generate(self):
        """ Returns a new sequence number for the adapted object
        """


class IRedirector(Interface):
    """An adapter for the BrowserRequest to redirect a user after loading the
    next page to a specific URL which is opened in another window / tab with
    the name "target".
    """

    def redirect(url, target='_blank'):
        """Redirects the user to a `url` which is opened in a window called
        `target` after loading the next page.
        """

    def get_redirects(remove=True):
        """Returns a list of dicts containing the redirect informations. If
        `remove` is set to `True` (default) the redirect infos are deleted.
        """


class IUniqueNumberUtility(Interface):
    """The unique number utility provides the a dynamic counter functionality,
    for the given object and keyword-arguments.
    It generates a unique key for every keywoards and values combination,
    including the portal_type except the keyword 'portal_type' is given.
    For every key he provide the get_number and remove_number functioniality.
    """

    def get_number(self, obj, **keys):
        """Return the stored value for the combinated key, if no entry exists,
        it generates one with the help of the unique number generator.
        """

    def remove_number(self, obj, **keys):
        """Remove the entry in the local storage for the combinated key.
        """


class IUniqueNumberGenerator(Interface):
    """The unique nuber generator adapter, handle for every key a counter with
    the highest assigned value. So he provides the generate functionality,
    which return the next number, for every counter.
    """

    def generate(self, key):
        """Return the next number for the given key.
        """


class IRepositoryPathSourceBinderQueryModificator(Interface):
    """Markerinterface for RepositoryPathSourceBinderQueryModificator
    adapter"""

    def modify_query(self, query):
        """Modify the ReppositoryPathSourceBinderQuery"""
