from Acquisition import aq_base
from five import grok
from opengever.base import _
from opengever.base.behaviors.utils import split_string_by_numbers
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.dossier.behaviors.dossier import IDossierMarker
from persistent.dict import PersistentDict
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces._content import IFolderish
from zope.annotation.interfaces import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
import re


DOSSIER_KEY = 'dossier_reference_mapping'
REPOSITORY_FOLDER_KEY = 'repository_reference_mapping'

CHILD_REF_KEY = 'reference_numbers'
PREFIX_REF_KEY = 'reference_prefix'


class ReferenceNumberPrefixAdpater(grok.Adapter):
    """This Adapter handles the whole Reference number prefix assignment"""

    grok.provides(IReferenceNumberPrefix)
    grok.context(IFolderish)

    def __init__(self, context):
        self.context = context

    def get_reference_mapping(self, obj=None):
        type_key = self.get_type_key(obj)
        annotations = IAnnotations(self.context)

        if not annotations.get(type_key):
            annotations[type_key] = PersistentDict({})
        return annotations[type_key]

    def get_child_mapping(self, obj=None):
        reference_mapping = self.get_reference_mapping(obj)
        if not reference_mapping.get(CHILD_REF_KEY, None):
            reference_mapping[CHILD_REF_KEY] = PersistentDict()
        return reference_mapping.get(CHILD_REF_KEY, None)

    def get_prefix_mapping(self, obj=None):
        reference_mapping = self.get_reference_mapping(obj)
        if not reference_mapping.get(PREFIX_REF_KEY, None):
            reference_mapping[PREFIX_REF_KEY] = PersistentDict()
        return reference_mapping.get(PREFIX_REF_KEY, None)

    def get_type_key(self, obj=None):
        if obj and IDossierMarker.providedBy(obj):
            return DOSSIER_KEY
        return REPOSITORY_FOLDER_KEY

    def get_first_number(self, obj=None):
        if self.get_type_key(obj) == DOSSIER_KEY:
            return u'1'

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReferenceNumberSettings)
        return proxy.reference_prefix_starting_point

    def get_next_number(self, obj=None):
        """ return the next possible reference number for object
        at the actual context
        """

        child_mapping = self.get_child_mapping(obj)

        if not child_mapping.keys():
            # It's the first number ever issued
            return self.get_first_number(obj)
        else:
            prefixes_in_use = child_mapping.keys()
            # Sort the list of unicode strings *numerically*
            prefixes_in_use.sort(key=split_string_by_numbers)
            lastnumber = prefixes_in_use[-1]

            # if its a number, we increase the whole number
            try:
                lastnumber = int(lastnumber)
                return unicode(lastnumber + 1)
            except ValueError:
                pass

            # .. otherwise try to increment the last numeric part
            xpr = re.compile('\d+')
            matches = tuple(xpr.finditer(lastnumber))
            if len(matches) > 0:
                span = matches[-1].span()
                subvalue = lastnumber[span[0]:span[1]]
                try:
                    subvalue = int(subvalue)
                except (ValueError, TypeError):
                    pass
                else:
                    subvalue += 1
                    subvalue = unicode(subvalue)
                    lastnumber = lastnumber[:span[0]] + \
                        subvalue + lastnumber[span[1]:]
                    return lastnumber
            else:
                return u''

    def get_number(self, obj):
        """return the reference number for the object,
        if no number is registred for this obj, we generate a new one.

        """
        intids = getUtility(IIntIds)
        try:
            intid = intids.getId(aq_base(obj))
        # In some cases we might not have an intid yet.
        except KeyError:
            return None

        prefix_mapping = self.get_prefix_mapping(obj)
        if intid in prefix_mapping:
            return prefix_mapping.get(intid)
        return None

    def set_number(self, obj, number=None):
        """Store the number in the Annotations,
        If number is None, we get the standard value
        """
        intids = getUtility(IIntIds)
        intid = intids.getId(aq_base(obj))

        if not number:
            number = self.get_next_number(obj)

        if not isinstance(number, unicode):
            number = unicode(number)

        self.get_prefix_mapping(obj)[intid] = number
        self.get_child_mapping(obj)[number] = intid
        return number

    def is_valid_number(self, number, obj=None):
        """ check the given reference number for the given context """

        child_mapping = self.get_child_mapping(obj)
        if number not in child_mapping.keys():
            return True

        elif obj is not None:
            # check if the given object has the given number ever
            intids = getUtility(IIntIds)
            intid = intids.getId(aq_base(obj))

            if child_mapping[number] == intid:
                return True

        return False

    def is_prefix_used(self, prefix):
        """ Checks if prefix is in use"""
        if not isinstance(prefix, unicode):
            prefix = unicode(prefix)
        return prefix in self.get_reference_mapping()['reference_prefix'].values()

    def get_number_mapping(self):
        items = []
        intid_util = getUtility(IIntIds)

        for prefix, intid in self.get_child_mapping().iteritems():
            try:
                title = intid_util.getObject(intid).effective_title
            except KeyError:
                # if a repositoryfolder is already removed the intid
                # utility raises an KeyError. But the number should still
                # be in the list, because it should be available to remove
                # via the reference prefix manager.
                title = _('label_already_removed',
                          '-- Already removed object --')

            items.append({'prefix': prefix,
                          'title': title,
                          'active': (self.get_prefix_mapping()[intid] == prefix)})

        def key_sorter(obj):
            key = obj['prefix']
            if (key.isdigit()):
                return int(key)
            return key

        return sorted(items, key=key_sorter)

    def free_number(self, prefix):
        if not isinstance(prefix, unicode):
            prefix = unicode(prefix)

        if self.is_prefix_used(prefix):
            raise Exception("Prefix is in use.")

        if prefix in self.get_child_mapping().keys():
            self.get_child_mapping().pop(prefix)
