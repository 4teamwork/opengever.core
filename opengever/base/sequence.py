from opengever.base.interfaces import INoSeparateConnectionForSequenceNumbers
from opengever.base.interfaces import ISequenceNumber
from opengever.base.interfaces import ISequenceNumberGenerator
from opengever.base.protect import unprotected_write
from opengever.setup.interfaces import IDuringSetup
from persistent.dict import PersistentDict
from plone.dexterity.interfaces import IDexterityContent
from Products.CMFCore.interfaces import ISiteRoot
from ZODB.DemoStorage import DemoStorage
from ZODB.POSException import ConflictError
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.interface import implementer
import logging
import transaction


SEQUENCE_NUMBER_ANNOTATION_KEY = 'ISequenceNumber.sequence_number'
LOG = logging.getLogger('opengever.base.sequence')


@implementer(ISequenceNumber)
class SequenceNumber(object):
    """ The sequence number utility provides a getNumber(obj) method
    which returns a unique number for each object.
    """

    def get_number(self, obj):
        ann = unprotected_write(IAnnotations(obj))
        if SEQUENCE_NUMBER_ANNOTATION_KEY not in ann.keys():
            generator = getAdapter(obj, ISequenceNumberGenerator)
            value = generator.generate()
            ann[SEQUENCE_NUMBER_ANNOTATION_KEY] = value
        return ann.get(SEQUENCE_NUMBER_ANNOTATION_KEY)

    def remove_number(self, obj):
        ann = unprotected_write(IAnnotations(obj))
        if SEQUENCE_NUMBER_ANNOTATION_KEY in ann.keys():
            del ann[SEQUENCE_NUMBER_ANNOTATION_KEY]


@implementer(ISequenceNumberGenerator)
@adapter(IDexterityContent)
class DefaultSequenceNumberGenerator(object):
    """ Provides a default sequence number generator.
    The portal_type of the object is used as *unique-key*
    """

    def __init__(self, context):
        self.context = context

    def generate(self):
        return self.get_next(self.key)

    @property
    def key(self):
        return u'DefaultSequenceNumberGenerator.%s' % self.context.portal_type

    def get_next(self, key):
        return SequenceNumberIncrementer()(key)


class SequenceNumberIncrementer(object):
    """The sequence number increment creates and returns the next
    sequence number for a given key when called.

    It does this in a separate connection to the ZODB.
    When the integer value is returned, the incrementation is
    already committed and the value will be unique and not raise
    any conflict when committing the main transaction of the
    requesting code.

    This behavior is important in order to eliminate conflicts of
    content-creation request and to provide safe, unique sequence
    numbers.
    When the requesting transaction is aborted or repeated, the
    sequence number which was requested in this transaction will
    not be used, which results in gaps in the sequence numbering
    system. These gaps are expected and accepted.
    """

    maximum_retries = 10

    def __call__(self, sequence_number_key):
        portal = getUtility(ISiteRoot)
        request = getRequest()

        if isinstance(portal._p_jar.db().storage, DemoStorage):
            # We use DemoStorage (probably in tests), which
            # do not allow concurrent DB connections,
            # thus we don't spawn a new database connection.
            return self._increment_number(portal, sequence_number_key)

        if any([IDuringSetup.providedBy(request),
                INoSeparateConnectionForSequenceNumbers.providedBy(request)]):
            # During setup, the Plone site will just have been created in that
            # very transaction. That means it's not available for us to fetch
            # from a separate ZODB connection during setup. So no separate
            # ZODB connection for sequence numbers during setup.
            #
            # In addition, there's other cases where we don't want to use
            # a separate connection to issue sequence numbers, like during
            # OGGBundle import
            return self._increment_number(portal, sequence_number_key)

        return self._separate_zodb_connection(
            self._increment_number,
            sequence_number_key)

    def _increment_number(self, portal, key):
        ann = unprotected_write(IAnnotations(portal))
        if SEQUENCE_NUMBER_ANNOTATION_KEY not in ann:
            ann[SEQUENCE_NUMBER_ANNOTATION_KEY] = unprotected_write(
                PersistentDict())

        mapping = unprotected_write(ann.get(SEQUENCE_NUMBER_ANNOTATION_KEY))
        if key not in mapping:
            mapping[key] = 0

        mapping[key] += 1
        return mapping[key]

    def _separate_zodb_connection(self, callback, *args, **kwargs):
        main_connection_portal = getUtility(ISiteRoot)
        manager = transaction.TransactionManager()
        connection = main_connection_portal._p_jar.db().open(
            transaction_manager=manager)
        try:

            for _r in range(self.maximum_retries):
                manager.begin()
                portal = connection[main_connection_portal._p_oid]
                result = callback(portal, *args, **kwargs)

                try:
                    manager.commit()
                except ConflictError:
                    LOG.info('SequenceNumberIncrementer'
                             ' ConflictError; retrying')
                    manager.abort()
                else:
                    return result

            # Maximum retries exceeded, raise conflict to main
            # transaction / actual request.
            raise

        finally:
            connection.close()
