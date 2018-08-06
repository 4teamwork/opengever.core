from opengever.base.formutils import group_by_name
from opengever.testing import IntegrationTestCase
from plone.dexterity.browser.add import DefaultAddForm
from plone.supermodel import model
from z3c.form.form import Form
from zope.schema import TextLine


class IPerson(model.Schema):

    model.fieldset(
        u'personal',
        label=u'Personal Details',
        fields=[u'firstname', u'lastname'],
    )

    firstname = TextLine(title=u'First Name')
    lastname = TextLine(title=u'Last Name')


class IAddress(model.Schema):

    model.fieldset(
        u'address',
        label=u'Home Address',
        fields=[u'street', u'city'],
    )

    street = TextLine(title=u'Street')
    city = TextLine(title=u'City and postal code')


class IWorkplace(model.Schema):

    model.fieldset(
        u'workplace',
        label=u'Workplace Details',
        fields=[u'company_name'],
    )

    company_name = TextLine(title=u'Company Name')


class IEmployee(IPerson, IAddress, IWorkplace):
    """Test schema with three different fieldsets.
    """


class EmployeeAddForm(DefaultAddForm):

    schema = IEmployee


class TestFormUtils(IntegrationTestCase):

    def setUp(self):
        super(TestFormUtils, self).setUp()
        self.context = None

    def test_group_by_name_rejects_non_group_forms(self):
        form = Form(self.context, self.request)
        with self.assertRaises(Exception):
            group_by_name(form, 'foo_group')

    def test_group_by_name_returns_none_if_no_such_group(self):
        form = EmployeeAddForm(self.context, self.request)
        self.assertIsNone(group_by_name(form, 'group_that_doesnt_exist'))

    def test_group_by_name_returns_correct_group(self):
        self.login(self.regular_user)

        form = EmployeeAddForm(self.portal, self.request)
        form.update()

        group = group_by_name(form, 'personal')
        self.assertEquals('personal', group.__name__)
        self.assertEquals('Personal Details', group.label)

        group = group_by_name(form, 'address')
        self.assertEquals('address', group.__name__)
        self.assertEquals('Home Address', group.label)

        group = group_by_name(form, 'workplace')
        self.assertEquals('workplace', group.__name__)
        self.assertEquals('Workplace Details', group.label)
