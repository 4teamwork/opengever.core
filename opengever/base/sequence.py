from five import grok
from persistent.dict import PersistentDict
from plone.dexterity.interfaces import IDexterityContent
from Products.CMFCore.interfaces import ISiteRoot
from Products.Transience.Transience import Increaser
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility, getAdapter

from opengever.base.interfaces import ISequenceNumber
from opengever.base.interfaces import ISequenceNumberGenerator

SEQUENCE_NUMBER_ANNOTATION_KEY = 'ISequenceNumber.sequence_number'


class SequenceNumber(grok.GlobalUtility):
    """ The sequence number utility provides a getNumber(obj) method
    which returns a unique number for each object.
    """
    grok.provides(ISequenceNumber)

    def get_number(self, obj):
        ann = IAnnotations(obj)
        if SEQUENCE_NUMBER_ANNOTATION_KEY not in ann.keys():
            generator = getAdapter(obj, ISequenceNumberGenerator)
            value = generator.generate()
            ann[SEQUENCE_NUMBER_ANNOTATION_KEY] = value
        return ann.get(SEQUENCE_NUMBER_ANNOTATION_KEY)

    def remove_number(self, obj):
        ann = IAnnotations(obj)
        if SEQUENCE_NUMBER_ANNOTATION_KEY in ann.keys():
            del ann[SEQUENCE_NUMBER_ANNOTATION_KEY]


class DefaultSequenceNumberGenerator(grok.Adapter):
    """ Provides a default sequence number generator.
    The portal_type of the object is used as *unique-key*
    For choosing the number the
    Products.Transience.Transience.Increaser should be used. See:
    http://pyyou.wordpress.com/2009/12/09/how-to-add-a-counter-without-conflict-error-in-zope/
    """

    grok.provides(ISequenceNumberGenerator)
    grok.context(IDexterityContent)

    def generate(self):
        return self.get_next(self.key)

    @property
    def key(self):
        return u'DefaultSequenceNumberGenerator.%s' % self.context.portal_type

    def get_next(self, key):
        portal = getUtility(ISiteRoot)
        ann = IAnnotations(portal)
        if SEQUENCE_NUMBER_ANNOTATION_KEY not in ann.keys():
            ann[SEQUENCE_NUMBER_ANNOTATION_KEY] = PersistentDict()
        map = ann.get(SEQUENCE_NUMBER_ANNOTATION_KEY)
        if key not in map:
            map[key] = Increaser(0)
        # increase
        inc = map[key]
        inc.set(inc() + 1)
        map[key] = inc
        return inc()
