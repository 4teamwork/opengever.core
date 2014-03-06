from five import grok
from itertools import izip_longest
from opengever.base.interfaces import IReferenceNumberFormatter
from zope.interface import Interface
import re


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

    def sorter(self, brain_or_value):
        """ Converts the "reference" into a tuple containing integers,
        which are converted well. Sorting "10" and "2" as strings
        results in wrong order.
        """
        if not isinstance(brain_or_value, basestring):
            value = brain_or_value.reference
        else:
            value = brain_or_value

        splitter = re.compile('[/\., ]')
        if not isinstance(value, str) and not isinstance(
            value, unicode):
            return value
        parts = []
        for part in splitter.split(value):
            part = part.strip()
            try:
                part = int(part)
            except ValueError:
                pass
            parts.append(part)
        return parts


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

    def sorter(self, brain_or_value):
        if not isinstance(brain_or_value, basestring):
            # It's a brain
            value = brain_or_value.reference
        else:
            # It's already a string value
            value = brain_or_value

        clientid_repository_separator = u' '

        # '010.123.43-1.1-7'  -->  '010.123.43', '1.1-7'
        clientid, remainder = value.split(clientid_repository_separator, 1)
        refnums_part, remainder = remainder.split(self.repository_dossier_seperator, 1)

        # Return a tuple with the different parts separated.
        # Cast document and (sub)dossier parts to integers to achieve proper
        # sorting, but keep the refnum part as a string because it is already
        # zero-padded and sorting it numerically would yield wrong results.

        if remainder.count(self.dossier_document_seperator) > 0:
            # Document Reference Number
            dossier_part, document_part = remainder.split(self.dossier_document_seperator, 1)
            subdossier_parts = [int(d) for d in dossier_part.split('.')]
            return (refnums_part, tuple(subdossier_parts), int(document_part))
        else:
            # Dossier Reference Number
            dossier_part = remainder
            subdossier_parts = [int(d) for d in dossier_part.split('.')]
            return (refnums_part, tuple(subdossier_parts))


class NoClientIdDottedReferenceFormatter(DottedReferenceFormatter):
    grok.name('no_client_id_dotted')

    def complete_number(self, numbers):
            """DottedReferenceFormatter which omits client id.
            """

            reference_number = u''

            if self.repository_number(numbers):
                reference_number = self.repository_number(numbers)

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
