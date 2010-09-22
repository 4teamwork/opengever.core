from five import grok
from opengever.ogds.base.exceptions import TransportationError
from opengever.ogds.base.interfaces import IDataCollector
from opengever.ogds.base.interfaces import IObjectCreator
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.utils import remote_request, remote_json_request
from plone.dexterity.interfaces import IDexterityFTI, IDexterityContent
from plone.dexterity.utils import createContentInContainer, iterSchemata
from plone.namedfile.interfaces import INamedFileField
from zope import schema
from zope.component import getAdapters, queryAdapter, getAdapter
from zope.component import getUtility
from zope.interface import Interface
import DateTime
import base64
import datetime
import json


BASEDATA_KEY = 'basedata'
REQUEST_KEY = 'object_data'


_marker = object()


class Transporter(grok.GlobalUtility):
    """ The transporter utility is able to copy objects to other
    clients.
    """

    grok.provides(ITransporter)

    def transport_to(self, obj, target_cid, container_path):
        """ Copies a *object* to another client (*target_cid*).
        """

        container_path = container_path.startswith('/') and \
            container_path[1:] or container_path

        jsondata = json.dumps(self._extract_data(obj))

        request_data = {
            REQUEST_KEY : jsondata,
            }
        return remote_request(target_cid, '@@transporter-receive-object',
                              path=container_path,
                              data=request_data)

    def transport_from(self, container, source_cid, path):
        """ Copies the object under *path* from client with *source_cid* into
        the local folder *container*
        """

        # remove beginning slashes from path
        if path[0]=='/':
            path = path[1:]

        data = remote_json_request(source_cid,
                                   '@@transporter-extract-object-json',
                                   path=path)

        obj = self._create_object(container, data)
        return obj

    def receive(self, container, request):
        jsondata = request.get(REQUEST_KEY)
        data = json.loads(jsondata)
        obj = self._create_object(container, data)
        return obj

    def extract(self, obj):
        """ Returns a JSON dump of *obj*
        """
        return json.dumps(self._extract_data(obj))

    def _extract_data(self, obj):
        """ Serializes a object
        """
        data = {}
        # base data
        creator = self._get_object_creator(obj.portal_type)
        data[BASEDATA_KEY] = creator.extract(obj)
        # collect data
        collectors = getAdapters((obj,), IDataCollector)
        for name, collector in collectors:
            data[name] = collector.extract()
        return data

    def _create_object(self, container, data):
        """ Creates the object with the data
        """
        portal_type = data[BASEDATA_KEY]['portal_type']
        # base data
        creator = self._get_object_creator(portal_type)
        obj = creator.create(container, data[BASEDATA_KEY])
        # insert data from collectors
        collectors = getAdapters((obj,), IDataCollector)
        for name, collector in collectors:
            collector.insert(data[name])
        return obj

    def _get_object_creator(self, portal_type):
        # get the FTI
        fti = getUtility(IDexterityFTI, name=portal_type)
        # do we have a specific one?
        creator = queryAdapter(fti, IObjectCreator, name=portal_type)
        if not creator:
            creator = getAdapter(fti, IObjectCreator, name='')
        return creator


class ReceiveObject(grok.CodeView):
    """The `ReceiveObject` view receives a object-transporter request on the
    target client and creates or updates the object.
    """

    grok.name('transporter-receive-object')
    grok.require('cmf.AddPortalContent')
    grok.context(Interface)

    def render( self ):
        transporter = getUtility(ITransporter)
        container = self.context
        return transporter.receive(container, self.request)


class ExtractObject(grok.CodeView):
    """The `ExtractObject` view is called by the transporter on a specific
    context on the source client for extract the data and returning it to
    the receiver.
    """

    grok.name('transporter-extract-object-json')
    grok.require('cmf.AddPortalContent')
    grok.context(Interface)

    def render(self):
        transporter = getUtility(ITransporter)
        return transporter.extract(self.context)


class DexterityObjectCreator(grok.Adapter):
    """Default adapter for creating dexterity objects. This adapter is used
    by the transporter utility for creating a object.
    The `IObjectCreator` adapts the FTI. This makes it possible to also support
    other FTI types such as Archetypes.
    """

    grok.context(IDexterityFTI)
    grok.provides(IObjectCreator)
    grok.name('')

    def extract(self, obj):
        return {
            'id': obj.getId(),
            'title': obj.Title(),
            'portal_type': obj.portal_type,
            }

    def create(self, container, data):
        return createContentInContainer(container=container,
                                        portal_type=data['portal_type'],
                                        checkConstraints=True,
                                        id=data['title'],
                                        title=data['title'])


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
            for name, field in schema.getFieldsInOrder( schemata ):
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
                value = subdata[name]
                value = self.unpack(name, field, value)
                if value!=_marker:
                    setattr(repr, name, value)

    def pack(self, name, field, value):
        """Packs the field data and makes it ready for transportation with
        json, which does only support basic data types.
        """
        if self._provided_by_one_of( field, [
                schema.interfaces.IDate,
                schema.interfaces.ITime,
                schema.interfaces.IDatetime,
                ]):
            if value:
                return str( value )
        elif self._provided_by_one_of( field, [
                INamedFileField,
                ] ):
            if value:
                return {
                    'filename' : value.filename,
                    'data' : base64.encodestring( value.data ),
                    }
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
                dt = DateTime.DateTime(value).parts()[:-1]
                return datetime.datetime(*dt)

        if self._provided_by_one_of(field, [INamedFileField,]):
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
