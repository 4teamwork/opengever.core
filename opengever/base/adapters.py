from Acquisition import aq_base
from five import grok
from opengever.base.behaviors.utils import split_string_by_numbers
from opengever.base.interfaces import IReferenceNumberPrefix
from persistent.dict import PersistentDict
from Products.CMFCore.interfaces._content import IFolderish
from zope.annotation.interfaces import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
import re


class ReferenceNumberPrefixAdpater(grok.Adapter):
    """This Adapter handles the whole Reference number prefix assignment"""

    grok.provides(IReferenceNumberPrefix)
    grok.context(IFolderish)

    # a mapping numbers : intids - never deleted
    CHILD_REF_KEY = 'reference_numbers'

    # a mapping intid : reference_number
    REF_KEY = 'reference_prefix'

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)

        #child mapping
        self.child_mapping = annotations.get(self.CHILD_REF_KEY, None)
        if self.child_mapping is None:
            self.child_mapping = PersistentDict()
            annotations[self.CHILD_REF_KEY] = self.child_mapping

        #reference prefix
        self.reference_mapping = annotations.get(self.REF_KEY, None)
        if self.reference_mapping is None:
            self.reference_mapping = PersistentDict()
            annotations[self.REF_KEY] = self.reference_mapping

    def get_next_number(self):
        """ return the next possible reference number for object
        at the actual context
        """
        if not self.child_mapping.keys():
            # It's the first number ever issued
            return u'1'
        else:
            prefixes_in_use = self.child_mapping.keys()
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
        if intid in self.reference_mapping:
            return self.reference_mapping.get(intid)
        return None

    def set_number(self, obj, number=None):
        """Store the number in the Annotations,
        If number is None, we get the standard value
        """
        intids = getUtility(IIntIds)
        intid = intids.getId(aq_base(obj))

        if not number:
            number = self.get_next_number()

        if not isinstance(number, unicode):
            number = unicode(number)

        self.reference_mapping[intid] = number
        self.child_mapping[number] = intid

        return number

    def is_valid_number(self, number, obj=None):
        """ check the given reference number for the given context """
        if number not in self.child_mapping.keys():
            return True

        elif obj is not None:
            # check if the given object has the given number ever
            intids = getUtility(IIntIds)
            intid = intids.getId(aq_base(obj))

            if self.child_mapping[number] == intid:
                return True

        return False
