from opengever.virusscan import _
from zope import schema
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


clamdConnectionType = SimpleVocabulary(
    [SimpleTerm(title=u"Unix Socket", value="socket"),
     SimpleTerm(title=u"Network", value="net")]
)


class IAVScannerSettings(Interface):
    """ Schema for the clamav settings
    """

    scan_before_download = schema.Bool(
        title=u'Scan for viruses before file download',
        description=u'Whether a virus check should be performed when '
                    u'downloading a file from Gever'
                    u'Note that this requires a correct configuration of the '
                    u'virus scanner (see IAVScannerSettings)',
        default=False)

    scan_on_upload = schema.Bool(
        title=u'Scan for viruses before file upload',
        description=u'Whether a virus check should be performed when '
                    u'uploading a file to Gever.'
                    u'Note that this requires a correct configuration of the '
                    u'virus scanner (see IAVScannerSettings)',
        default=False)

    clamav_connection = schema.Choice(
        title=u"Connection type to clamd",
        description=u"Choose whether clamd is accessible through local "
                    u"UNIX sockets or network.",
        vocabulary=clamdConnectionType)

    clamav_socket = schema.ASCIILine(
        title=u"Clamd local socket file",
        description=u"If connected to clamd through local UNIX sockets, "
                    u"the path to the local socket file.",
        default='/var/run/clamd',
        required=True)

    clamav_host = schema.ASCIILine(title=u"Scanner host",
                                   description=u"If connected to clamd "
                                               u"through the network, "
                                               u"the host running clamd.",
                                   default='localhost',
                                   required=True)

    clamav_port = schema.Int(title=u"Scanner port",
                             description=u"If connected to clamd "
                                         u"through the network, the "
                                         u"port on which clamd listens.",
                             default=3310,
                             required=True)

    clamav_timeout = schema.Int(title=u"Timeout",
                                description=u"The timeout in seconds for "
                                            u"communication with clamd.",
                                default=120,
                                required=True)


class IAVScanner(Interface):
    def ping():
        pass

    def scanBuffer(buffer):
        pass

    def scanStream(buffer):
        pass
