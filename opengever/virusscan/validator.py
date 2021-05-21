from opengever.virusscan import _
from opengever.virusscan.interfaces import IAVScanner
from opengever.virusscan.interfaces import IAVScannerSettings
from opengever.virusscan.scanner import ScanError
from plone import api
from plone.formwidget.namedfile.interfaces import INamedFileWidget
from plone.formwidget.namedfile.validator import NamedFileWidgetValidator
from plone.namedfile.interfaces import INamedField
from plone.registry.interfaces import IRegistry
from six import BytesIO
from z3c.form import validator
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import Invalid
import logging

logger = logging.getLogger('opengever.virusscan.uploads')

SCAN_RESULT_BASE_KEY = 'opengever.virusscan.scan_result'


def scanStream(stream):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IAVScannerSettings, check=False)
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


def validateStream(filename, filelike, request):
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
        message = translate(_(
                u'validation_failed',
                default=u"Validation failed, file is virus-infected. (${result})",
                mapping={u"result": result}
            ),
            context=request
        )
        logger.warning("{} filename: {}".format(message, filename))
        raise Invalid(message)


def validateDownloadIfNecessary(filename, file, request):
    # if scanning is disabled for download, we skip
    if not api.portal.get_registry_record(name='scan_before_download',
                                          interface=IAVScannerSettings):
        return True
    validateStream(filename, file.open(), request)


def validateUploadForFieldIfNecessary(fieldname, filename, filelike, request):
    # if scanning is disabled for upload, we skip
    if not api.portal.get_registry_record(name='scan_before_upload',
                                          interface=IAVScannerSettings):
        return True

    # Get a previous scan result on this REQUEST if there is one - to
    # avoid scanning the same upload twice.
    SCAN_RESULT_KEY = "{}.{}".format(SCAN_RESULT_BASE_KEY, fieldname)
    annotations = IAnnotations(request)
    scan_result = annotations.get(SCAN_RESULT_KEY, None)
    if scan_result is not None:
        logger.debug("File already scanned in this request")
        return scan_result
    try:
        validateStream(filename, filelike, request)
    except Invalid as e:
        annotations[SCAN_RESULT_KEY] = e.message
        raise e
    annotations[SCAN_RESULT_KEY] = True
    logger.info("No virus detected in {}".format(filename))
    return annotations[SCAN_RESULT_KEY]


class Z3CFormclamavValidator(NamedFileWidgetValidator):
    """z3c.form validator to confirm a file upload is virus-free."""

    def validate(self, value):
        super(Z3CFormclamavValidator, self).validate(value)

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

        return validateUploadForFieldIfNecessary(
            self.field.getName(), filename, filelike, self.request)


validator.WidgetValidatorDiscriminators(Z3CFormclamavValidator,
                                        field=INamedField,
                                        widget=INamedFileWidget)
