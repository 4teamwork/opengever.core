from zope.annotation.interfaces import IAnnotations
from five import grok
from opengever.base.interfaces import IUniqueNumberUtility
from opengever.base.interfaces import IUniqueNumberGenerator
from zope.component import getAdapter
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

COUNTER_START = 1
COUNTER_ADDITION_VALUE = 1


class UniqueNumberUtility(grok.GlobalUtility):
    """The unique number utility provides the a dynamic counter functionality,
    for the given object and keyword-arguments.
    It generates a unique key for every keywoards and values combination,
    including the portal_type except the keyword 'portal_type' is given.
    For every key he provide the get_number and remove_number functioniality.
    """

    grok.provides(IUniqueNumberUtility)

    def get_number(self, obj, **keys):
        """Return the stored value for the combinated key, if no entry exists,
        it generates one with the help of the unique number generator.
        """

        key = self.get_key(obj, keys)

        ann = IAnnotations(obj)
        if key not in ann.keys():
            portal_url = getToolByName(obj, 'portal_url')
            generator = getAdapter(
                portal_url.getPortalObject(), IUniqueNumberGenerator)
            value = generator.generate(key)
            ann[key] = value
        return ann.get(key)

    def get_key(self, obj, keys):

        # include the portal_type in to the combinated key,
        # when the keyword argument 'portal_type' is not given.
        if 'portal_type' not in keys:
            keys['type'] = obj.portal_type

        return ':'.join(['%s-%s' % (k, v) for (k, v) in keys.items()])

    def remove_number(self, obj, **keys):
        """Remove the entry in the local storage for the combinated key.
        """
        key = self.get_key(obj, keys)

        ann = IAnnotations(obj)
        if key in ann.keys():
            del ann[key]


class UniqueNumberUtilityGenerator(grok.Adapter):
    """The unique nuber generator adapter, handle for every key a counter with
    the highest assigned value. So he provides the generate functionality,
    which return the next number, for every counter.
    """

    grok.provides(IUniqueNumberGenerator)
    grok.context(IPloneSiteRoot)

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context)

    def generate(self, key):
        """Return the next number for the given key.
        """

        if key in self.annotations.keys():
            value = self.annotations[key] + COUNTER_ADDITION_VALUE
            self.annotations[key] = value
            return value
        else:
            self.annotations[key] = COUNTER_START
            return self.annotations[key]
