from itertools import izip_longest
from opengever.base.interfaces import IReferenceNumberFormatter
from opengever.ogds.base.utils import get_current_admin_unit
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
import re

split_numbers_pattern = re.compile('(\\d+)')


def transform_string_for_natural_sorting(reference_number):
    """Adds zero paddings to all numeric parts in a string to allow
    natural sorting.
    'client1' -> 'client00000001'
    'a1.2' -> 'a00000001.00000002'
    """
    parts = split_numbers_pattern.split(reference_number)
    padded_parts = []
    for part in parts:
        if not part:
            continue
        if part.isdigit():
            padded_parts.append(part.zfill(8))
        else:
            padded_parts.append(part.lower())
    return "".join(padded_parts)


@implementer(IReferenceNumberFormatter)
@adapter(Interface)
class DottedReferenceFormatter(object):
    """Provide dotted-nested reference numbers for repository tree items."""

    is_grouped_by_three = False

    repository_dossier_seperator = u' / '
    dossier_document_seperator = u' / '
    repository_title_seperator = u'.'

    def __init__(self, context):
        self.context = context

    @staticmethod
    def to_sortable_numbers(numbers):
        """Adds zero-padding to number parts in the numbers dictionary.
        {'site': ['client1'],
         'repository': ['3', '5'],
         'dossier: ['3', '10']'}
        becomes
        {'site': ['client00000001'],
         'repository': ['00000003', '00000005'],
         'dossier: ['00000003', '00000010']'}
        """
        return {ref_type: [transform_string_for_natural_sorting(number) for number in parts]
                for ref_type, parts in numbers.items()}

    def complete_sortable_number(self, numbers):
        """Generate the complete sortable reference number, for the given
        numbers dict. Zero paddings are added wherever necessary to make
        the number sortable
        """
        return self.complete_number(self.to_sortable_numbers(numbers))

    def complete_number(self, numbers):
        """Generate the complete reference number, for the given numbers
        dict.
        """
        reference_number = u' '.join(numbers.get('site', []))

        if self.location_prefix(numbers):
            reference_number = u'%s %s' % (
                self.location_prefix(numbers),
                reference_number,
                )

        if self.repositoryroot_addendum(numbers):
            reference_number = u'%s %s' % (reference_number, self.repositoryroot_addendum(numbers))

        if self.repository_number(numbers):
            if reference_number:
                reference_number = u'%s %s' % (
                    reference_number,
                    self.repository_number(numbers),
                    )
            else:
                reference_number = self.repository_number(numbers)

        if self.dossier_number(numbers):
            reference_number = u'%s%s%s' % (
                reference_number,
                self.repository_dossier_seperator,
                self.dossier_number(numbers),
                )

        if self.document_number(numbers):
            reference_number = u'%s%s%s' % (
                reference_number,
                self.dossier_document_seperator,
                self.document_number(numbers),
                )

        return reference_number.encode('utf-8')

    def location_prefix(self, numbers):
        """Return the location prefix of the context."""
        location_prefix = numbers.get('location_prefix')
        if location_prefix:
            return ''.join(location_prefix)
        return None

    def repositoryroot_addendum(self, numbers):
        return u''.join(numbers.get('repositoryroot', []))

    def repository_number(self, numbers):
        """Generate the reposiotry reference number part.
        Seperate every part with a dot.

        Example: 3.5.7.1.4
        """
        return u'.'.join(numbers.get('repository', []))

    def dossier_number(self, numbers):
        """Generate the dossier reference number part,
        Seperate every part with a dot.

        Example: 3.2.1
        """
        return u'.'.join(numbers.get('dossier', []))

    def document_number(self, numbers):
        """Generate the document reference number part.
        """
        return u'.'.join(numbers.get('document', []))

    def sorter(self, brain_or_value):
        """Converts the "reference" into a tuple containing integers,
        which are converted well. Sorting "10" and "2" as strings
        results in wrong order.
        """
        if not isinstance(brain_or_value, basestring):
            value = brain_or_value.reference

        else:
            value = brain_or_value

        splitter = re.compile(r'[/\., ]')

        if not isinstance(value, str) and not isinstance(value, unicode):
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

    def get_portal_part(self):
        """Returns the reference number part of the portal, the adminunit's
        abbreviation.
        """
        return get_current_admin_unit().abbreviation

    def list_to_string(self, reference_list):
        """Converts a list with the different objects parts in to a string:

        [[1, 4, 5], [452, 4], [135]] would return `1.4.5 / 452.4 / 135`.

        The list format is used by the OGGBundle format.
        """
        numbers = {
            'site': [self.get_portal_part()],
            }

        if reference_list:
            numbers['repository'] = map(str, reference_list[0])

        if len(reference_list) > 1:
            numbers['dossier'] = map(str, reference_list[1])

        if len(reference_list) > 2:
            numbers['document'] = map(str, reference_list[2])

        return self.complete_number(numbers)


class GroupedByThreeReferenceFormatter(DottedReferenceFormatter):
    """Referencenumber formatter, which groups three parts together
    and seperated them by point.

    134.3-2.1
    """

    is_grouped_by_three = True

    repository_dossier_seperator = u'-'
    dossier_document_seperator = u'-'
    repository_title_seperator = u''

    def repository_number(self, numbers):
        parts = numbers.get('repository', [])

        return '.'.join([
            ''.join(aa)
            for aa in self.grouper(parts, 3)
            ])

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

        # 'OG 010.123.43-1.1-7'  -->  '010.123.43-1.1-7'
        remainder = value.split(clientid_repository_separator, 1)[1]

        if self.repository_dossier_seperator in remainder:
            # Dossier or document reference number
            # '010.123.43-1.1-7'  -->  '010.123.43', '1.1-7'
            refnums_part, remainder = remainder.split(
                self.repository_dossier_seperator, 1)

        else:
            # Repofolder-only reference number
            # Nothing left to do, should already be sortable as string
            return remainder

        # Return a tuple with the different parts separated.
        # Cast document and (sub)dossier parts to integers to achieve proper
        # sorting, but keep the refnum part as a string because it is already
        # zero-padded and sorting it numerically would yield wrong results.

        if remainder.count(self.dossier_document_seperator) > 0:
            # Document Reference Number
            dossier_part, document_part = remainder.split(
                self.dossier_document_seperator, 1)

            subdossier_parts = [int(d) for d in dossier_part.split('.')]

            return (refnums_part, tuple(subdossier_parts), int(document_part))

        # Dossier Reference Number
        dossier_part = remainder
        subdossier_parts = [int(d) for d in dossier_part.split('.')]

        return (refnums_part, tuple(subdossier_parts))


class NoClientIdDottedReferenceFormatter(DottedReferenceFormatter):
    """Provide client id omitted dotted-nested reference numbers for repository
    tree items.
    """

    def get_portal_part(self):
        """Returns the reference number part of the portal, the adminunit's
        abbreviation.
        """
        return

    def complete_number(self, numbers):
        """Omit client id in this DottedReferenceFormatter."""
        reference_number = u''

        if self.location_prefix(numbers):
            reference_number = self.location_prefix(numbers)

        if self.repositoryroot_addendum(numbers):
            reference_number = u'%s %s' % (reference_number, self.repositoryroot_addendum(numbers))

        if self.repository_number(numbers):
            if reference_number:
                reference_number = u'%s %s' % (
                    reference_number,
                    self.repository_number(numbers),
                    )
            else:
                reference_number = self.repository_number(numbers)

        if self.dossier_number(numbers):
            reference_number = u'%s%s%s' % (
                reference_number,
                self.repository_dossier_seperator,
                self.dossier_number(numbers),
                )

        if self.document_number(numbers):
            reference_number = u'%s%s%s' % (
                reference_number,
                self.dossier_document_seperator,
                self.document_number(numbers),
                )

        return reference_number.encode('utf-8')


# XXX Refactor me and avoid copy-paste of complete_number.
class NoClientIdGroupedByThreeFormatter(GroupedByThreeReferenceFormatter):
    """Provide client id omitted group-by-three reference numbers for
    repository tree items.
    """

    def complete_number(self, numbers):
        """A client id omitting GroupedByThreeFormatter."""
        reference_number = u''

        if self.location_prefix(numbers):
            reference_number = self.location_prefix(numbers)

        if self.repositoryroot_addendum(numbers):
            reference_number = u'%s %s' % (reference_number, self.repositoryroot_addendum(numbers))

        if self.repository_number(numbers):
            if reference_number:
                reference_number = u'%s %s' % (
                    reference_number,
                    self.repository_number(numbers),
                    )
            else:
                reference_number = self.repository_number(numbers)

        if self.dossier_number(numbers):
            reference_number = u'%s%s%s' % (
                reference_number,
                self.repository_dossier_seperator,
                self.dossier_number(numbers),
                )

        if self.document_number(numbers):
            reference_number = u'%s%s%s' % (
                reference_number,
                self.dossier_document_seperator,
                self.document_number(numbers),
                )

        return reference_number.encode('utf-8')

    def sorter(self, brain_or_value):
        if not isinstance(brain_or_value, basestring):
            # It's a brain
            value = brain_or_value.reference

        else:
            # It's already a string value
            value = brain_or_value

        if self.repository_dossier_seperator in value:
            # '010.123.43-1.1-7'  -->  '010.123.43', '1.1-7'
            refnums_part, remainder = value.split(
                self.repository_dossier_seperator, 1)

        else:
            # Repofolder-only reference number
            # Nothing left to do, should already be sortable as string
            return value

        # Return a tuple with the different parts separated.
        # Cast document and (sub)dossier parts to integers to achieve proper
        # sorting, but keep the refnum part as a string because it is already
        # zero-padded and sorting it numerically would yield wrong results.

        if remainder.count(self.dossier_document_seperator) > 0:
            # Document Reference Number
            dossier_part, document_part = remainder.split(
                self.dossier_document_seperator, 1)

            subdossier_parts = [int(d) for d in dossier_part.split('.')]

            return (refnums_part, tuple(subdossier_parts), int(document_part))

        # Dossier Reference Number
        dossier_part = remainder
        subdossier_parts = [int(d) for d in dossier_part.split('.')]

        return (refnums_part, tuple(subdossier_parts))

    def get_portal_part(self):
        """Returns the reference number part of the portal, the adminunit's
        abbreviation.
        """
        return
