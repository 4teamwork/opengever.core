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
    latest_participations = ViewPageTemplateFile(
        'templates/latest_participations.pt')

    def __init__(self, context, request):
        super(OrganizationView, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        return self.template()

    def get_actor_link(self, archive):
        return Actor.lookup(archive.actor_id).get_link()

    def get_org_roles(self):
        query = OrgRole.query.filter_by(organization=self.context.model)
        return query.join(Person).order_by(
            Person.lastname, Person.firstname).all()

    def participations_fetch_url(self):
        return self.context.model.get_url('participations/list')

    def latest_participations_template(self):
        return self.latest_participations()
