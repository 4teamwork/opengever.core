from opengever.base import _
from zope import schema
from zope.interface import Interface


class IBaseCustodyPeriods(Interface):
    custody_periods = schema.List(title=u"custody period",
                                  default=[u'0',
                                           u'10',
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


class IBaseSettings(Interface):
    """Base settings
    """

    vocabulary_disabled_communities = schema.List(
         title=_(u'label_vocabulary_disabled_communities',
                 default=u'Vocabulary: disabled communities'),
         description=_(u'help_vocabulary_disabled_communities',
                       default=u'Select the terms from the communities '
                       'vocabulary which should not be selectable any more.'),
         value_type=schema.Choice(
            vocabulary=u'opengever.base.communities'),
         required=False)

    vocabulary_disabled_directorates = schema.List(
        title=_(u'label_vocabulary_disabled_directorates',
             default=u'Vocabulary: disabled directorates'),
        description=_(u'help_vocabulary_disabled_directorates',
                   default=u'Select the entries from the vocabulary which '
                   'should not be selectable any more.'),
        value_type=schema.Choice(
            vocabulary=u'opengever.base.directorates'),
             required=False)