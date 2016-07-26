from opengever.base.model import create_session
from opengever.base.response import JSONResponse
from opengever.base.utils import to_safe_html
from opengever.contact import _
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


class IRelatedEntityCRUDActions(Interface):

    def list():
        """Returns json list of all objects for the current context (contact).
        'plone/person-3/{viewname}/list'
        """

    def update():
        """Updates the entity attributes, with the one given by
        the request parameter.
        The view expect that its called by traversing over the related entity:
        `plone/person-3/{viewname}/14/update` for example.
        """

    def delete():
        """Remove the given object.
        The view expect that its called by traversing over the related entity:
        `plone/person-3/{viewname}/14/delete` for example.
        """

    def add():
        """Add a new object to the database
        'plone/person-3/{viewname}/add'
        """


class RelatedEntityCRUDView(BrowserView):
    """BaseView for CRUD endpoint view for all related entities
    (Addresses, MailAddresses, PhoneNumbers and URLs).
    """
    implements(IBrowserView, IPublishTraverse, IRelatedEntityCRUDActions)

    model = None
    contact_backref_name = ''

    def publishTraverse(self, request, name):
        if name in IRelatedEntityCRUDActions.names():
            return getattr(self, name)

        # we only support exactly one id
        if self.object_id:
            raise NotFound

        try:
            self.object_id = int(name)
        except ValueError:
            raise NotFound

        self.object = self.model.query.get(self.object_id)

        if not self.object:
            raise NotFound

        if self.object.contact is not self.contact:
            # Prevent from cross injections
            raise NotFound

        return self

    def __init__(self, context, request):
        super(RelatedEntityCRUDView, self).__init__(context, request)
        self.contact = self.context.model
        self.object_id = None
        self.object = None
        self.session = create_session()

    def list(self):
        objs = [number.serialize() for number in
                getattr(self.contact, self.contact_backref_name)]

        return JSONResponse(self.request).data(objects=objs).dump()

    @property
    def attributes(self):
        """A list of all attribute names(String) which are definable.
        """
        raise NotImplemented

    def add(self):
        data = {}
        for attr in self.attributes:
            data[attr] = to_safe_html(self.request.get(attr))

        error_msg = self._validate(**data)

        if error_msg:
            return JSONResponse(self.request).error(error_msg).dump()

        obj = self.model(contact_id=self.context.model.person_id, **data)
        self.session.add(obj)

        msg = _(
            u'msg_info_object_added',
            u'The object was added successfully')

        return JSONResponse(self.request).info(msg).proceed().dump()

    def update(self):
        data = {}
        for attr in self.attributes:
            data[attr] = to_safe_html(
                self.request.get(attr, getattr(self.object, attr)))

        error_msg = self._validate(**data)
        if error_msg:
            return JSONResponse(self.request).error(error_msg).dump()

        for key, value in data.items():
            setattr(self.object, key, value)

        return JSONResponse(self.request).info(
            _('msg_object_updated',
              default=u"Object updated.")).proceed().dump()

    def delete(self):
        self.object.delete()

        return JSONResponse(self.request).info(
            _(u'msg_object_deleted',
              default=u'Object successfully deleted')).dump()

    def _validate(self, **kwargs):
        """Validates the given attributes.

        Returns None if the validation passed.
        Returns the errormessage if the validation failed.
        """

        return None
