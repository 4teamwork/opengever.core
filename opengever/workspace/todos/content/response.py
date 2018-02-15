from datetime import datetime
from opengever.workspace.interfaces import IResponse
from opengever.workspace.interfaces import IResponses
from opengever.workspace.interfaces import IToDo
from opengever.workspace.todos.content import annotation_data_list
from opengever.workspace.todos.utils import get_current_user_id
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements


class Response(annotation_data_list.ItemWrapperBase):
    implements(IResponse)

    def __init__(self,
                 text,
                 created=None,
                 creator=None,
                 modified=None,
                 modifier=None):
        super(Response, self).__init__(
            text=text,
            created=created or datetime.now(),
            creator=creator or get_current_user_id(),
            modified=modified,
            modifier=modifier)

    def __setattr__(self, name, value):
        super(Response, self).__setattr__(name, value)
        if name == 'text':
            self.modifier = get_current_user_id()
            self.modified = datetime.now()


@adapter(IToDo)
@implementer(IResponses)
class Responses(annotation_data_list.AnnotationDataListBase):

    annotations_key = 'opengever.workspace.todos:responses'
    item_class = Response
    writeable_attributes = ('text',)
