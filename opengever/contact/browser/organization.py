from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.contact import _
from opengever.contact.browser.person import IAddressRow
from opengever.contact.browser.person import IMailAddressRow
from opengever.contact.browser.person import IPhoneNumberRow
from opengever.contact.models import OrgRole
from opengever.contact.models import Person
from opengever.contact.models import Organization
from opengever.ogds.base.actor import Actor
from plone.supermodel import model
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


from collective.z3cform.datagridfield import BlockDataGridFieldFactory
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from opengever.base.browser.modelforms import ModelAddForm
from opengever.base.browser.modelforms import ModelEditForm
from opengever.base.handlebars import prepare_handlebars_template
from opengever.contact.models import Address
from opengever.contact.models import MailAddress
from opengever.contact.models import Organization
from opengever.contact.models import OrgRole
from opengever.contact.models import PhoneNumber
from opengever.contact.models.person import Person
from opengever.ogds.base.actor import Actor
from path import Path
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import field
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


class OrganizationView(BrowserView):
    """Overview for a Organization SQL object.
    """

    implements(IBrowserView, IPublishTraverse)

    template = ViewPageTemplateFile('templates/organization.pt')
    latest_participations = ViewPageTemplateFile(
        'templates/latest_participations.pt')

    def __init__(self, context, request):
        super(OrganizationView, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        return self.template()

    def get_actor_link(self, archive):
        return Actor.lookup(archive.actor_id).get_link()

    def get_org_roles(self, active):
        query = OrgRole.query.filter_by(organization=self.context.model)
        query = query.join(Person).filter(Person.is_active == active)
        return query.order_by(Person.lastname, Person.firstname).all()

    def get_active_org_roles(self):
        return self.get_org_roles(active=True)

    def get_inactive_org_roles(self):
        return self.get_org_roles(active=False)

    def participations_fetch_url(self):
        return self.context.model.get_url('participations/list')

    def latest_participations_template(self):
        return self.latest_participations()


class IOrganizationModel(model.Schema):
    """Organization model schema interface."""

    name = schema.TextLine(
        title=_(u"label_name", default=u"Name"),
        max_length=CONTENT_TITLE_LENGTH,
        required=False)

    phone_numbers = schema.List(
        title=_(u'label_phone_numbers', default=u'Phone numbers'),
        required=False,
        value_type=DictRow(title=u"tablerow", schema=IPhoneNumberRow))

    mail_addresses = schema.List(
        title=_(u'label_mail_addresses', default=u'Mail addresses'),
        required=False,
        value_type=DictRow(title=u"tablerow", schema=IMailAddressRow))

    addresses = schema.List(
        title=_(u'label_addresses', default=u'Addresses'),
        required=False,
        value_type=DictRow(title=u"tablerow", schema=IAddressRow))


class AddOrganization(ModelAddForm):
    schema = IOrganizationModel
    model_class = Organization

    label = _('Add Person', default=u'Add Person')

    def nextURL(self):
        return self._created_object.get_url()

    def updateWidgets(self):
        self.fields['phone_numbers'].widgetFactory = DataGridFieldFactory
        self.fields['mail_addresses'].widgetFactory = DataGridFieldFactory
        self.fields['addresses'].widgetFactory = BlockDataGridFieldFactory
        super(AddOrganization, self).updateWidgets()

    def create(self, data):
        self.validate(data)

        addresses = data.pop('addresses')
        phone_numbers = data.pop('phone_numbers')
        mail_addresses = data.pop('mail_addresses')

        organization = self.model_class(**data)

        for address_data in addresses:
            Address(contact=organization, **address_data)

        for phone_data in phone_numbers:
            PhoneNumber(contact=organization, **phone_data)

        for mail_data in mail_addresses:
            MailAddress(contact=organization, **mail_data)

        return organization
