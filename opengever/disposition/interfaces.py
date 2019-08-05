from zope import schema
from zope.interface import Interface


class IAppraisal(Interface):
    """The appraisal adapter Interface."""


class IHistoryStorage(Interface):
    """The history storage adapter Interface."""


class IDisposition(Interface):
    """The disposition Interface."""


class IDuringDossierDestruction(Interface):
    """Request layer to indicate that dossiers are currently being destroyed.
    """


class ISIPTransport(Interface):
    """A specific transport for delivering SIP packages.

    Transports will be registered as named adapters, and their name will be
    used by the DeliveryScheduler to track delivery status.
    """

    def __init__(disposition, request, parent_logger):
        """A transport adapts a disposition, request and a parent_logger.

        The parent_logger should be used by the transport for logging. Either
        by reparenting its own logger to it (which the BaseTransport class
        does for convenience) or by using it directly to log.

        This is so that e.g. during nightly jobs the transporter's log
        messages can be captured and written to the logfile as well by the
        NightlyJobRunner's log handler.
        """

    def deliver():
        """Perform the delivery using the mechanism implemented by this transport.

        Error signalling by the transport should be done using exceptions.
        The return value of this method will be ignored.
        """

    def is_enabled():
        """Whether this transport is enabled or not.

        Only enabled transports will be invoked for scheduled deliveries, and
        a delivery will also only be scheduled for a particular transport if
        that transport is active at the time of SIP generation.
        """


class IFilesystemTransportSettings(Interface):

    enabled = schema.Bool(
        title=u'Enabled',
        description=u'Whether FilesystemTransport is enabled or not.',
        default=False)

    destination_directory = schema.TextLine(
        title=u'Destination directory',
        description=u'Directory into which SIP packages should be delivered.',
        default=u'')
