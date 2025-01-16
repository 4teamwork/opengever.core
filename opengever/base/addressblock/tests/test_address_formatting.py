from opengever.base.addressblock import AddressBlockData
from opengever.testing import IntegrationTestCase
from textwrap import dedent


def addr(text):
    return dedent(text.lstrip('\n')).strip()


class TestAddressFormatting(IntegrationTestCase):

    def test_private_address(self):
        block = AddressBlockData(
            salutation=u'Herr',
            academic_title=u'Dr.',
            first_name=u'Fridolin',
            last_name=u'M\xfcller',

            street_and_no=u'Murtenstrasse 42',
            postal_code=u'3008',
            city=u'Bern',
        )

        expected = addr(u"""
        Herr
        Dr. Fridolin M\xfcller
        Murtenstrasse 42
        3008 Bern
        """)
        self.assertEqual(expected, block.format())

    def test_private_address_with_extra_lines(self):
        block = AddressBlockData(
            salutation=u'Herr',
            academic_title=u'Dr.',
            first_name=u'Fridolin',
            last_name=u'M\xfcller',

            street_and_no=u'Murtenstrasse 42',
            postal_code=u'3008',
            city=u'Bern',
            extra_line_1=u'c/o John Doe',
            extra_line_2=u'who knows what comes here'
        )

        expected = addr(u"""
        Herr
        Dr. Fridolin M\xfcller
        c/o John Doe
        who knows what comes here
        Murtenstrasse 42
        3008 Bern
        """)
        self.assertEqual(expected, block.format())

    def test_org_address(self):
        block = AddressBlockData(
            org_name=u'Fabasoft 4teamwork AG',

            street_and_no=u'Dammweg 9',
            postal_code=u'3013',
            city=u'Bern',
        )

        expected = addr(u"""
        Fabasoft 4teamwork AG
        Dammweg 9
        3013 Bern
        """)
        self.assertEqual(expected, block.format())

    def test_org_address_addressed_to_person(self):
        block = AddressBlockData(
            salutation=u'Herr',
            academic_title=u'Dr.',
            first_name=u'Fridolin',
            last_name=u'M\xfcller',

            org_name=u'Fabasoft 4teamwork AG',

            street_and_no=u'Dammweg 9',
            postal_code=u'3012',
            city=u'Bern',
        )

        expected = addr(u"""
        Fabasoft 4teamwork AG
        Herr Dr. Fridolin M\xfcller
        Dammweg 9
        3012 Bern
        """)
        self.assertEqual(expected, block.format())

    def test_org_address_addressed_to_person_with_extra_lines(self):
        block = AddressBlockData(
            salutation=u'Herr',
            academic_title=u'Dr.',
            first_name=u'Fridolin',
            last_name=u'M\xfcller',

            extra_line_1=u'en extra address line',
            org_name=u'Fabasoft 4teamwork AG',

            street_and_no=u'Dammweg 9',
            postal_code=u'3012',
            city=u'Bern',
        )

        expected = addr(u"""
        Fabasoft 4teamwork AG
        Herr Dr. Fridolin M\xfcller
        en extra address line
        Dammweg 9
        3012 Bern
        """)
        self.assertEqual(expected, block.format())

    def test_private_address_with_po_box(self):
        block = AddressBlockData(
            salutation=u'Herr',
            academic_title=u'Dr.',
            first_name=u'Fridolin',
            last_name=u'M\xfcller',

            po_box=u'Postfach',
            postal_code=u'3008',
            city=u'Bern 8',
        )

        expected = addr(u"""
        Herr
        Dr. Fridolin M\xfcller
        Postfach
        3008 Bern 8
        """)
        self.assertEqual(expected, block.format())

    def test_org_address_with_po_box(self):
        block = AddressBlockData(
            org_name=u'Fabasoft 4teamwork AG',

            po_box=u'Postfach',
            postal_code=u'3013',
            city=u'Bern 7',
        )

        expected = addr(u"""
        Fabasoft 4teamwork AG
        Postfach
        3013 Bern 7
        """)
        self.assertEqual(expected, block.format())

    def test_org_address_addressed_to_person_with_po_box(self):
        block = AddressBlockData(
            salutation=u'Herr',
            academic_title=u'Dr.',
            first_name=u'Fridolin',
            last_name=u'M\xfcller',

            org_name=u'Fabasoft 4teamwork AG',

            po_box=u'Postfach',
            postal_code=u'3013',
            city=u'Bern 7',
        )

        expected = addr(u"""
        Fabasoft 4teamwork AG
        Herr Dr. Fridolin M\xfcller
        Postfach
        3013 Bern 7
        """)
        self.assertEqual(expected, block.format())

    def test_academic_title_and_salutation_are_optional_for_private_address(self):
        block = AddressBlockData(
            salutation=None,
            academic_title=None,
            first_name=u'Fridolin',
            last_name=u'M\xfcller',

            street_and_no=u'Murtenstrasse 42',
            postal_code=u'3008',
            city=u'Bern',
        )

        expected = addr(u"""
        Fridolin M\xfcller
        Murtenstrasse 42
        3008 Bern
        """)
        self.assertEqual(expected, block.format())

    def test_academic_title_and_salutation_are_optional_for_org_address(self):
        block = AddressBlockData(
            salutation=None,
            academic_title=None,
            first_name=u'Fridolin',
            last_name=u'M\xfcller',

            org_name=u'Fabasoft 4teamwork AG',

            street_and_no=u'Dammweg 9',
            postal_code=u'3012',
            city=u'Bern',
        )

        expected = addr(u"""
        Fabasoft 4teamwork AG
        Fridolin M\xfcller
        Dammweg 9
        3012 Bern
        """)
        self.assertEqual(expected, block.format())

    def test_street_is_ignored_if_po_box_is_present(self):
        block = AddressBlockData(
            org_name=u'Fabasoft 4teamwork AG',

            street_and_no=u'Dammweg 9',
            po_box=u'Postfach',
            postal_code=u'3013',
            city=u'Bern 7',
        )

        # If 'po_box' is given, any value from 'street_and_no' will be
        # ignored. This might need to change in the future.

        expected = addr(u"""
        Fabasoft 4teamwork AG
        Postfach
        3013 Bern 7
        """)
        self.assertEqual(expected, block.format())

    def test_never_adds_switzerland_to_domestic_addresses(self):
        block = AddressBlockData(
            salutation=u'Herr',
            academic_title=u'Dr.',
            first_name=u'Fridolin',
            last_name=u'M\xfcller',

            street_and_no=u'Murtenstrasse 42',
            postal_code=u'3008',
            city=u'Bern',
            country=u'Schweiz',
        )

        expected = addr(u"""
        Herr
        Dr. Fridolin M\xfcller
        Murtenstrasse 42
        3008 Bern
        """)
        self.assertEqual(expected, block.format())

    def test_adds_country_to_foreign_addresses(self):
        block = AddressBlockData(
            salutation=u'Mr.',
            first_name=u'Bill',
            last_name=u'Gates',

            street_and_no=u'1 Microsoft Way',
            postal_code=u'98052',
            city=u'Redmond',
            country=u'United States of America',
        )

        expected = addr(u"""
        Mr.
        Bill Gates
        1 Microsoft Way
        98052 Redmond
        United States of America
        """)
        self.assertEqual(expected, block.format())

    def test_filters_none_values_and_empty_strings(self):
        block = AddressBlockData(
            first_name=u'Bill',
            last_name=u'Gates',
        )

        expected = addr(u"""
        Bill Gates
        """)
        self.assertEqual(expected, block.format())

    def test_private_address_when_hide_salutation_is_active(self):
        from opengever.base.addressblock.interfaces import IAddressBlockDataSettings
        from plone import api
        api.portal.set_registry_record('hide_salutation', True,
                                       interface=IAddressBlockDataSettings)
        block = AddressBlockData(
            salutation=u'Herr',
            academic_title=u'Dr.',
            first_name=u'Fridolin',
            last_name=u'M\xfcller',

            street_and_no=u'Murtenstrasse 42',
            postal_code=u'3008',
            city=u'Bern',
        )

        expected = addr(u"""
        Dr. Fridolin M\xfcller
        Murtenstrasse 42
        3008 Bern
        """)
        self.assertEqual(expected, block.format())
