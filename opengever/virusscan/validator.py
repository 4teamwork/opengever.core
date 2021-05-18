from collective.clamav import _
from collective.clamav.interfaces import IAVScanner
from collective.clamav.interfaces import IAVScannerSettings
from collective.clamav.scanner import ScanError
from plone.registry.interfaces import IRegistry
from Products.validation.interfaces.IValidator import IValidator
from six import BytesIO
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implements, Invalid
import logging

logger = logging.getLogger('collective.clamav.uploads')

SCAN_RESULT_KEY = 'collective.clamav.scan_result'


def scanStream(stream):

    registry = getUtility(IRegistry)
    settings = registry.forInterface(IAVScannerSettings, check=False)
    if settings is None or not settings.clamav_enabled:
        return ''
    scanner = getUtility(IAVScanner)

    if settings.clamav_connection == 'net':
        result = scanner.scanStream(
            stream, 'net',
            host=settings.clamav_host,
            port=int(settings.clamav_port),
            timeout=float(settings.clamav_timeout))
    else:
        result = scanner.scanStream(stream, 'socket',
                                    socketpath=settings.clamav_socket,
                                    timeout=float(settings.clamav_timeout))
    return result


def _scanBuffer(buffer):
    return scanStream(BytesIO(buffer))


class ClamavValidator:
    """Archetypes validator to confirm a file upload is virus-free."""

    implements(IValidator)

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        # Get a previous scan result on this REQUEST if there is one - to
        # avoid scanning the same upload twice.
        request = kwargs['REQUEST']
        if not request:
            # Not very modern, but plone.restapi's DeserializeFromJson doesn't
            # pass the request object to archetype validators
            request = getRequest()
        annotations = IAnnotations(request)
        scan_result = annotations.get(SCAN_RESULT_KEY, None)
        if scan_result is not None:
            logger.debug("File already scanned in this request")
            return scan_result

        if hasattr(value, 'seek'):
            # when submitted a new 'value' is a
            # 'ZPublisher.HTTPRequest.FileUpload'
            filelike = value
            filename = filelike.filename if hasattr(filelike, 'filename') else '<not known>'
        elif hasattr(value, 'getBlob'):
            # the value can be a plone.app.blob.field.BlobWrapper
            # in which case we open the blob file to provide a file interface
            # as used for FileUpload
            filelike = value.getBlob().open()
            filename = filelike.filename if hasattr(filelike, 'filename') else '<not known>'
        elif value:
            filelike = BytesIO(value)
            filename = '<stream>'
        else:
            # value is falsy - assume we kept existing file
            return True

        if isinstance(filename, unicode):
            filename = filename.encode('utf-8')
        filelike.seek(0)
        result = ''
        try:
            result = scanStream(filelike)
        except ScanError as e:
            logger.error('ScanError %s on %s.' % (e, filename))
            return _(u'error_while_scanning',
                     default=u"There was an error while checking the file for "
                     u"viruses: Please contact your system administrator.")

        if result:
            annotations[SCAN_RESULT_KEY] = translate(_(
                    u'validation_failed',
                    default=u"Validation failed, file is virus-infected. (${result})",
                    mapping={u"result": result}
                ),
                context=request
            )
            logger.warning("{} filename: {}".format(
                annotations[SCAN_RESULT_KEY],
                filename
            ))
        else:
            annotations[SCAN_RESULT_KEY] = True
            logger.info("No virus detected in {}".format(filename))

        return annotations[SCAN_RESULT_KEY]


try:
    from z3c.form import validator
    from plone.namedfile.interfaces import INamedField
    from plone.formwidget.namedfile.interfaces import INamedFileWidget
    from plone.formwidget.namedfile.validator import NamedFileWidgetValidator
except ImportError:
    pass
else:

    class Z3CFormclamavValidator(NamedFileWidgetValidator):
        """z3c.form validator to confirm a file upload is virus-free."""

        def validate(self, value):
            super(Z3CFormclamavValidator, self).validate(value)

            # Get a previous scan result on this REQUEST if there is one - to
            # avoid scanning the same upload twice.
            annotations = IAnnotations(self.request)
            scan_result = annotations.get(SCAN_RESULT_KEY, None)
            if scan_result is not None:
                logger.debug("File already scanned in this request")
                return scan_result

            if hasattr(value, 'seek'):
                # when submitted a new 'value' is a
                # 'ZPublisher.HTTPRequest.FileUpload'
                filelike = value
                filename = filelike.filename if hasattr(filelike, 'filename') else '<not known>'
            elif hasattr(value, 'open'):
                # the value can be a NamedBlobFile / NamedBlobImage
                # in which case we open the blob file to provide a file interface
                # as used for FileUpload
                filelike = value.open()
                filename = filelike.filename if hasattr(filelike, 'filename') else '<not known>'
            elif value:
                filelike = BytesIO(value)
                filename = '<stream>'
            else:
                # value is falsy - assume we kept existing file
                return True

            if isinstance(filename, unicode):
                filename = filename.encode('utf-8')
            filelike.seek(0)
            result = ''
            try:
                result = scanStream(filelike)
            except ScanError as e:
                logger.error('ScanError %s on %s.' % (e, filename))
                raise Invalid(
                    _(u'error_while_scanning',
                      default="There was an error while checking the file for "
                              "viruses: Please contact your system administrator.")
                )

            if result:
                annotations[SCAN_RESULT_KEY] = translate(_(
                        u'validation_failed',
                        default=u"Validation failed, file is virus-infected. (${result})",
                        mapping={u"result": result}
                    ),
                    context=self.request
                )
                logger.warning("{} filename: {}".format(
                    annotations[SCAN_RESULT_KEY],
                    filename
                ))
                raise Invalid(annotations[SCAN_RESULT_KEY])
            else:
                annotations[SCAN_RESULT_KEY] = True
                logger.info("No virus detected in {}".format(filename))
                return True

    validator.WidgetValidatorDiscriminators(Z3CFormclamavValidator,
                                            field=INamedField,
                                            widget=INamedFileWidget)
