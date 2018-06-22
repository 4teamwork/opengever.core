from opengever.base import advancedjson
from opengever.base.request import dispatch_request


class Connector(object):
    """The connector connects two objects and executes a dispatched action
    for each connected object.

    The use-case of this class is the following:

    We have a Proposal and a Submitted Proposal. They don't know each other but
    they are related in some kind.

    Another class, the SQL Proposal knows the paths for this objects.

    If we want to change something on the Proposal, we also want to change it
    on the Submitted Proposal and vice versa.

    The connector does exactly this. It connects the two objects. And later,
    you can dispatch some actions. The dispatched actions are executed for each
    connected object.
    """
    actions = {}

    @classmethod
    def register(cls, klass):
        assert klass.action_id() not in cls.actions
        cls.actions[klass.action_id()] = klass
        return klass

    def __init__(self):
        self.paths = []

    def connect_path(self, path):
        self.paths.append(path)

    def dispatch(self, action, **data):
        for connector_path in self.paths:
            request_data = {'data': advancedjson.dumps({
                'action': action.action_id(),
                'data': data
            })}

            response = dispatch_request(
                connector_path.admin_unit_id,
                '@@receive-connector-action',
                path=connector_path.path,
                data=request_data,)

            self.validate_response(response)

    @classmethod
    def receive(cls, context, request):
        data = advancedjson.loads(request.get('data'))
        action = cls.actions.get(data.get('action'))
        return action(context, request, data.get('data')).execute()

    def validate_response(self, response):
        response_body = response.read()
        if response_body != 'OK':
            raise ValueError(
                'Unexpected response {!r} when validating response.'.format(
                    response_body))


class ConnectorPath(object):
    """Use ConnectorPaths to connect different objects thorugh the Connector
    class.
    """
    def __init__(self, admin_unit_id, path):
        self.path = path
        self.admin_unit_id = admin_unit_id


class ConnectorAction(object):
    """A connector action is something that should be excecuted on every
    connected object.
    """

    def __init__(self, context, request, data):
        self.context = context
        self.request = request
        self.data = data

    def execute(self):
        raise NotImplementedError

    @classmethod
    def action_id(cls):
        return cls.__name__.decode('utf-8')
