from five import grok
from opengever.base.exceptions import TransportationError
from opengever.base.interfaces import IDataCollector
from opengever.base.request import dispatch_json_request
from opengever.base.security import elevated_privileges
from opengever.ogds.base.utils import decode_for_json
from opengever.ogds.base.utils import encode_after_json
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.dexterity.utils import iterSchemata
from plone.namedfile.interfaces import INamedFileField
from z3c.relationfield.interfaces import IRelation
from z3c.relationfield.interfaces import IRelationChoice
from z3c.relationfield.interfaces import IRelationList
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zope.component import getAdapters
from zope.component import getUtility
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
import base64
import DateTime
import json


BASEDATA_KEY = 'basedata'
FIELDDATA_KEY = 'field-data'
REQUEST_KEY = 'object_data'
REQUIRED_SCHEMA_KEYS = ('ITask', 'IForwarding',)

ORIGINAL_INTID_ANNOTATION_KEY = 'transporter_original-intid'


_marker = object()


class Transporter(object):
    """ The transporter objects is able to copy objects to other
    clients.
    """

    def transport_to(self, obj, target_cid, container_path,
                     view='transporter-receive-object', **data):
        """ Copies an *object* to another client (*target_cid*).
        """

        jsondata = json.dumps(self.extract(obj))

        request_data = {
            REQUEST_KEY: jsondata,
            }
        request_data.update(**data)

        return dispatch_json_request(
            target_cid, '@@{}'.format(view),
            path=container_path, data=request_data)

    def transport_from(self, container, source_cid, path):
        """ Copies the object under *path* from client with *source_cid* into
        the local folder *container*
        *path* is the relative path of the object to its plone site root.
        """

        data = dispatch_json_request(source_cid,
                                     '@@transporter-extract-object-json',
                                     path=path)

        return self.create(data, container)

    def _extract_data(self, request):
        return json.loads(request.get(REQUEST_KEY))

    def receive(self, container, request):
        return self.create(self._extract_data(request), container)

    def extract(self, obj):
        return DexterityObjectDataExtractor(obj).extract()

    def create(self, data, container):
        return DexterityObjectCreator(data).create_in(container)

    def update(self, obj, request):
        return DexterityObjectUpdater(self._extract_data(request)).update(obj)


class ReceiveObject(grok.View):
    """Receives a JSON serialized object and creates or updates an instance
    within its context.

    It returns JSON containing the created object's path and intid.
    """

    grok.name('transporter-receive-object')
    grok.require('cmf.AddPortalContent')
    grok.context(Interface)

    def render(self):
        obj = self.receive()
        portal = self.context.portal_url.getPortalObject()
        portal_path = '/'.join(portal.getPhysicalPath())

        intids = getUtility(IIntIds)

        data = {
            'path': '/'.join(obj.getPhysicalPath())[
                len(portal_path) + 1:],
            'intid': intids.queryId(obj)
            }

        # Set correct content type for JSON response
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(data)

    def receive(self):
        transporter = Transporter()
        container = self.context
        return transporter.receive(container, self.request)


class PrivilegedReceiveObject(ReceiveObject):
    """Same functionality as the ReceiveObject view, but creates the content
    with elevated privileges.
    """

    grok.name('transporter-privileged-receive-object')
    grok.require('cmf.AddPortalContent')
    grok.context(Interface)

    def receive(self):
        transporter = Transporter()
        container = self.context
        with elevated_privileges():
            return transporter.receive(container, self.request)


class ExtractObject(grok.View):
    """Extract data from its context and returns a JSON serialized object.
    """

    grok.name('transporter-extract-object-json')
    grok.require('cmf.AddPortalContent')
    grok.context(Interface)

    def render(self):
        # Set correct content type for JSON response
        self.request.response.setHeader("Content-type", "application/json")

        return json.dumps(Transporter().extract(self.context))


class DexterityObjectCreator(object):

    def __init__(self, data):
        self.data = encode_after_json(data)
        self.portal_type = self.data[BASEDATA_KEY]['portal_type']
        self.title = self.data[BASEDATA_KEY].pop('title')
        if not isinstance(self.title, unicode):
            self.title = self.title.decode('utf-8')

    #XXX use plone.api
    def create_in(self, container):
        obj = createContent(self.portal_type, title=self.title)
        notify(ObjectCreatedEvent(obj))

        # insert data from collectors
        collectors = getAdapters((obj.__of__(container),), IDataCollector)
        for name, collector in collectors:
            collector.insert(self.data[name])

        obj = addContentToContainer(container, obj, checkConstraints=True)
        return obj


class DexterityObjectUpdater(DexterityObjectCreator):

    def update(self, obj):
        collectors = getAdapters((obj,), IDataCollector)
        for name, collector in collectors:
            collector.insert(self.data[name])

        notify(ObjectModifiedEvent(obj))


class DexterityObjectDataExtractor(object):

    def __init__(self, obj):
        self.obj = obj

    def extract(self):
        data = {}
        data[BASEDATA_KEY] = {'id': self.obj.getId(),
                              'title': self.obj.Title(),
                              'portal_type': self.obj.portal_type}

        # collect data
        collectors = getAdapters((self.obj,), IDataCollector)
        for name, collector in collectors:
            data[name] = collector.extract()

        return decode_for_json(data)


class DexterityFieldDataCollector(grok.Adapter):
    """The `DexterityFieldDataCollector` is used for extracting field data from
    a dexterity object and for setting it later on the target.
    This adapter is used by the transporter utility.
    """
    grok.context(IDexterityContent)
    grok.provides(IDataCollector)
    grok.name('field-data')

    def extract(self):
        """Extracts the field data and returns a dict of all data.
        """
        data = {}
        for schemata in iterSchemata(self.context):
            subdata = {}
            repr = schemata(self.context)
            for name, field in schema.getFieldsInOrder(schemata):
                value = getattr(repr, name, _marker)
                if value == _marker:
                    value = getattr(self.context, name, None)
                value = self.pack(name, field, value)
                subdata[name] = value
            if schemata.getName() in data.keys():
                raise TransportationError((
                        'Duplacte behavior names are not supported',
                        schemata.getName()))
            data[schemata.getName()] = subdata
        return data

    def insert(self, data):
        """Inserts the field data on self.context
        """
        for schemata in iterSchemata(self.context):
            repr = schemata(self.context)
            subdata = data[schemata.getName()]
            for name, field in schema.getFieldsInOrder(schemata):
                value = subdata.get(name, _marker)
                value = self.unpack(name, field, value)
                if value != _marker:
                    setattr(repr, name, value)

    def pack(self, name, field, value):
        """Packs the field data and makes it ready for transportation with
        json, which does only support basic data types.
        """
        if self._provided_by_one_of(field, [
                schema.interfaces.IDate,
                schema.interfaces.ITime,
                schema.interfaces.IDatetime,
                ]):
            if value:
                return str(value)
        elif self._provided_by_one_of(field, [
                INamedFileField,
                ]):
            if value:
                return {
                    'filename': value.filename,
                    'data': base64.encodestring(value.data),
                    }

        elif self._provided_by_one_of(field, (
                IRelation,
                IRelationChoice,
                IRelationList,)):
            # Remove all relations since we cannot guarantee anyway the they
            # are on the target. Relations have to be rebuilt by to tool which
            # uses the transporter - if required.
            if self._provided_by_one_of(field, (IRelation, IRelationChoice)):
                return None
            elif self._provided_by_one_of(field, (IRelationList,)):
                return []

        return value

    def unpack(self, name, field, value):
        """Unpacks the value from the basic json types to the objects which
        are stored on the field later.
        """
        if self._provided_by_one_of(field, [
                schema.interfaces.IDate,
                schema.interfaces.ITime,
                schema.interfaces.IDatetime,
                ]):
            if value:
                return DateTime.DateTime(value).asdatetime()

        if self._provided_by_one_of(field, [INamedFileField]):
            if value and isinstance(value, dict):
                filename = value['filename']
                data = base64.decodestring(value['data'])
                return field._type(data=data, filename=filename)
        return value

    def _provided_by_one_of(self, obj, ifaces):
        """Checks if at least one interface of the list `ifaces` is provied
        by the `obj`.
        """

        for ifc in ifaces:
            if ifc.providedBy(obj):
                return True
        return False


class OriginalIntidDataCollector(grok.Adapter):
    """This data collector stores the intid of the originally extracted
    object in the annotations of the copy. This is very important for being
    able to map the intids and fix relations.
    """

    grok.context(IDexterityContent)
    grok.provides(IDataCollector)
    grok.name('intid-data')

    def extract(self):
        intids = getUtility(IIntIds)
        return intids.getId(self.context)

    def insert(self, data):
        IAnnotations(self.context)[ORIGINAL_INTID_ANNOTATION_KEY] = data


class DublinCoreMetaDataCollector(grok.Adapter):
    """This data collector stores the standard dublin core data of
    plone objects, like the creation date or the creator.
    """

    grok.context(IDexterityContent)
    grok.provides(IDataCollector)
    grok.name('dublin-core')

    def extract(self):
        return {
            'creator': self.context.Creator(),
            'created': str(self.context.created()),
            }

    def insert(self, data):

        self.context.setCreators(data.get('creator'))

        self.context.creation_date = DateTime.DateTime(
            data.get('created'))
