from opengever.contact.models import OrgRole
from opengever.contact.models import Person
from opengever.ogds.base.actor import Actor
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


class OrganizationView(BrowserView):
    """Overview for a Organization SQL object.
    """

    implements(IBrowserView, IPublishTraverse)

    template = ViewPageTemplateFile('templates/organization.pt')

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
