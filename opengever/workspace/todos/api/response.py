from opengever.workspace.interfaces import IResponses
from opengever.workspace.todos.api import annotation_data_list_service


class Get(annotation_data_list_service.GETService):
    name = 'responses'
    data_list_adapter_interface = IResponses


class Post(annotation_data_list_service.POSTService):
    name = 'responses'
    data_list_adapter_interface = IResponses


class Patch(annotation_data_list_service.PATCHService):
    name = 'responses'
    data_list_adapter_interface = IResponses


class Delete(annotation_data_list_service.DELETEService):
    name = 'responses'
    data_list_adapter_interface = IResponses
