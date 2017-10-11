from Acquisition import aq_inner
from opengever.base.browser.helper import get_css_class
from opengever.globalindex.model.task import Task
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import ogds_service
from opengever.task import _
from opengever.task.adapters import IResponseContainer
from opengever.task.response import Base
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
import datetime


class ResponseView(ViewletBase, Base):

    def __init__(self, context, request, view, manager):
        ViewletBase.__init__(self, context, request, view, manager)
        Base.__init__(self, context, request)

    def responses(self):
        container = IResponseContainer(self.context)
        responses = []

        transforms = api.portal.get_tool(name='portal_transforms')
        for id, response in enumerate(container):
            info = dict(
                id=id,
                response=response,
                text=transforms.convertTo(
                    'text/html', response.text,
                    mimetype='text/x-web-intelligent'),
                edit_link=self.edit_link(id),
                delete_link=self.delete_link(id))

            responses.append(info)

        # sorting on date
        responses.sort(lambda a, b: cmp(b['response'].date,
                                    a['response'].date))

        return responses

    @property
    def can_edit(self):
        # TODO: this permission should renamed!!!
        return self.memship.checkPermission('Poi: Edit response',
                                            aq_inner(self.context))

    def edit_link(self, id):
        return '{}/@@task_response_edit?response_id={}'.format(
            self.context.absolute_url(), id)

    @property
    def can_delete(self):
        # TODO: should be solved with a separate permission
        return self.memship.checkPermission('Manage portal',
                                            aq_inner(self.context))

    def delete_link(self, id):
        return '{}/@@task_response_delete?response_id={}'.format(
            self.context.absolute_url(), id)

    def get_created_header(self):
        return _('transition_label_created', 'Created by ${user}',
                 mapping={
                     'user': Actor.lookup(self.context.Creator()).get_link()})

    def get_created_date(self):
        adapter = getMultiAdapter((self.context, self.request), name="plone")

        return adapter.toLocalizedTime(self.context.created(),
                                       long_format=True)

    def get_css_class(self, item):
        """used for display icons in the view"""
        return get_css_class(item)

    def get_added_objects(self, response):
        # Some relations may not have an added_object attribute...
        try:
            response.added_object
        except AttributeError:
            return None

        # .. and sometimes it may be empty.
        if not response.added_object:
            return None

        # Support for multiple added objects was added, so added_object may
        # be a list of relations, but could also be a relation directly.
        if hasattr(response.added_object, '__iter__'):
            relations = response.added_object
        else:
            relations = [response.added_object]

        # Return the target objects, not the relations.
        objects = []
        for rel in relations:
            objects.append(rel.to_object)
        return objects

    def get_added_successor(self, response):
        try:
            response.successor_oguid
        except AttributeError:
            return None
        if response.successor_oguid:
            return Task.query.by_oguid(response.successor_oguid)
        else:
            return None

    def convert_change_values(self, fieldname, value):
        if fieldname == 'responsible_client':
            org_unit = ogds_service().fetch_org_unit(value)
            if org_unit:
                return org_unit.label()
            else:
                return value

        elif fieldname == 'responsible':
            return Actor.lookup(value).get_link()

        elif isinstance(value, datetime.date):
            trans_service = getToolByName(
                self.context, 'translation_service')
            return trans_service.toLocalizedTime(
                datetime.datetime(value.year, value.month, value.day))

        return value
