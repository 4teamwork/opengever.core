from Acquisition import aq_base
from Products.CMFCore.interfaces._content import IFolderish
from five import grok
from opengever.base.interfaces import IReferenceNumberPrefix
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
import re


class ReferenceNumberPrefixAdpater(grok.Adapter):
    grok.provides(IReferenceNumberPrefix)
    grok.context(IFolderish)
    ANNO_KEY = 'reference_numbers'

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)
        self.__mapping = annotations.get(self.ANNO_KEY, None)
        if self.__mapping is None:
            self.__mapping = PersistentDict()
            annotations[self.ANNO_KEY] = self.__mapping

    def get_next_number(self):
        """ return the next possible reference number for object
        at the actual context
        """
        if self.__mapping.values():
            lastnumber = max(self.__mapping.values())

            # then increase by one, if possible:
            # if its a number, we increase the whole number
            # .. otherwise try to increment the last numeric part
            if isinstance(lastnumber, int):
                return lastnumber + 1
            else:
                xpr = re.compile('\d+')
                matches = tuple(xpr.finditer(lastnumber))
                if len(matches)>0:
                    span = matches[-1].span()
                    subvalue = lastnumber[span[0]:span[1]]
                    try:
                        subvalue = int(subvalue)
                    except (ValueError, TypeError):
                        pass
                    else:
                        subvalue += 1
                        subvalue = str(subvalue)
                        lastnumber = lastnumber[:span[0]] + \
                                        subvalue + lastnumber[span[1]:]
                        return lastnumber
                else:
                    return ''
        return 1

    def get_number(self, obj):
        """return the reference number for the object,
        if no number is registred for this obj, we generate a new one.
        """
        intids = getUtility(IIntIds)
        intid = intids.getId(aq_base(obj))
        if intid in self.__mapping:
            return self.__mapping.get(intid)
        else:
            return self.set_number(obj)

    def set_number(self, obj, number=None):
        """Store the number in the Annotations,
        If number is None, we get the standard value
        """
        intids = getUtility(IIntIds)
        intid = intids.getId(aq_base(obj))

        if not number:
            number = self.get_next_number()

        self.__mapping[intid] = number

        return number

    def is_valid_number(self, number):
        """ check the given reference number for the given context """
        if number not in self.__mapping.values():
            return True

        return False
