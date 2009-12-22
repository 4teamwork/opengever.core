from zope import schema
from zope.interface import Interface

# -*- extra stuff goes here -*-

class IBaseCustodyPeriods(Interface):
    custody_periods = schema.List(title=u"custody period", default=[u'0', u'10', u'30', u'100', u'150',])


class IRetentionPeriodRegister(Interface):
    """ plone.registry register for retention_period
    """
    retention_period = schema.List(title=u'retention period',
                                   default=[u'5',
                                            u'10',
                                            u'15',
                                            u'20',
                                            u'25'])

class IBaseClientID(Interface):
    client_id = schema.TextLine(title=u"client id", default=u"OG")


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
