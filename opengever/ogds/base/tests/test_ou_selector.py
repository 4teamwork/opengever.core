from opengever.ogds.base.ou_selector import CURRENT_ORG_UNIT_KEY
from opengever.ogds.base.ou_selector import NullOrgUnit
from opengever.ogds.base.ou_selector import OrgUnitSelector
from opengever.ogds.models.org_unit import OrgUnit
import inspect
import unittest2


class TestOrgUnitSelector(unittest2.TestCase):

    def setUp(self):
        self.unit_a = OrgUnit('clienta', title="Client A")
        self.unit_b = OrgUnit('clientb', title="Client B")
        self.unit_c = OrgUnit('clientc', title="Client C")

    def test_raise_value_error_when_callig_without_empty_unit_list(self):
        with self.assertRaises(ValueError) as cm:
            OrgUnitSelector({}, [])

        self.assertEquals(
            'The OrgUnitSelector needs at least one Unit.',
            str(cm.exception))

    def test_get_current_unit_returns_unit_which_is_storred_in_the_session(self):
        selector = OrgUnitSelector(
            {CURRENT_ORG_UNIT_KEY: 'clientb'},
            [self.unit_a, self.unit_b])

        self.assertEquals(self.unit_b, selector.get_current_unit())

    def test_get_current_unit_returns_fallback_unit_when_no_unit_is_storred(self):
        selector = OrgUnitSelector({}, [self.unit_a, self.unit_b])

        self.assertEquals(self.unit_a, selector.get_current_unit())

    def test_available_units_are_all_units(self):
        selector = OrgUnitSelector({},
            [self.unit_a, self.unit_b, self.unit_c])

        self.assertEquals([self.unit_a, self.unit_b, self.unit_c],
                          selector.available_units())

    def test_set_current_unit_updates_current_id(self):
        selector = OrgUnitSelector(
            {CURRENT_ORG_UNIT_KEY: 'clientb'},
            [self.unit_a, self.unit_b, self.unit_c])

        selector.set_current_unit('clienta')

        self.assertEquals(self.unit_a,
                          selector.get_current_unit())

    def test_set_current_unit_updates_activ_unit(self):
        selector = OrgUnitSelector(
            {CURRENT_ORG_UNIT_KEY: 'clientb'},
            [self.unit_a, self.unit_b, self.unit_c])

        selector.set_current_unit('clienta')

        self.assertEquals(self.unit_a, selector.get_current_unit())

    def test_null_org_unit_interface_implements_org_unit(self):
        ignore = ['assign_to_admin_unit']
        # cannot use `inspect.getmembers` since it triggers sqlalchemy magic
        method_names = [name for name, func in OrgUnit.__dict__.items()
                        if inspect.isfunction(func)
                        and not name.startswith('_')
                        and name not in ignore]

        for method_name in method_names:
            if not hasattr(NullOrgUnit, name):
                self.fail('Missing null-implementation: "NullOrgUnit.{}"'
                          .format(name))
