from zope import schema
from zope.interface import Interface


class IOpengeverBaseLayer(Interface):
    """Marker interfaces for opengever base browserview customisations.
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

    def get_number(self):
        """ Returns the reference number of the context
        """


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
