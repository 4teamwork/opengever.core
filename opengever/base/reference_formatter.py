from five import grok
from itertools import izip_longest
from opengever.base.interfaces import IReferenceNumberFormatter
from zope.interface import Interface


class DottedReferenceFormatter(grok.Adapter):

    grok.provides(IReferenceNumberFormatter)
    grok.context(Interface)
    grok.name('dotted')

    repository_dossier_seperator = u' / '
    dossier_document_seperator = u' / '
    repository_title_seperator = u'.'

    def complete_number(self, numbers):
        """Generate the complete reference number, for the given numbers dict.
        """

        reference_number = u' '.join(numbers.get('site', []))

        if self.repository_number(numbers):
            reference_number = u'%s %s' % (
                reference_number,
                self.repository_number(numbers))

        if self.dossier_number(numbers):
            reference_number = u'%s%s%s' % (
                reference_number,
                self.repository_dossier_seperator,
                self.dossier_number(numbers))

        if self.document_number(numbers):
            reference_number = u'%s%s%s' % (
                reference_number,
                self.dossier_document_seperator,
                self.document_number(numbers))

        return reference_number.encode('utf-8')

    def repository_number(self, numbers):
        """Generate the reposiotry reference number part.
        Seperate every part with a dot.

        Example: 3.5.7.1.4
        """
        return u'.'.join(numbers.get('repository', []))

    def dossier_number(self, numbers):
        """Generate the dossier reference number part,
        Seperate every part with a dot.

        Example: 3.2.1"""

        return u'.'.join(numbers.get('dossier', []))

    def document_number(self, numbers):
        """Generate the document reference number part.
        """
        return u'.'.join(numbers.get('document', []))


class GroupedByThreeReferenceFormatter(DottedReferenceFormatter):
    """Referencenumber formatter, which groups three parts together
    and seperated them by point.

    134.3-2.1
    """

    grok.provides(IReferenceNumberFormatter)
    grok.context(Interface)
    grok.name('grouped_by_three')

    repository_dossier_seperator = u'-'
    dossier_document_seperator = u'-'
    repository_title_seperator = u''

    def repository_number(self, numbers):

        parts = numbers.get('repository', [])

        return '.'.join(
            [''.join(aa) for aa in self.grouper(parts, 3)])

    def grouper(self, iterable, n, fillvalue=u''):
        args = [iter(iterable)] * n
        return list(izip_longest(fillvalue=fillvalue, *args))
