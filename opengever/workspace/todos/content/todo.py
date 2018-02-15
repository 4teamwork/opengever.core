from datetime import datetime
from opengever.workspace.interfaces import IToDo
from opengever.workspace.todos.utils import get_current_user_id
from plone import api
from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel.model import Schema
from zope.interface import implements
from zope.interface import provider
from zope.schema import Date
from zope.schema import Datetime
from zope.schema import List
from zope.schema import TextLine


@provider(IFormFieldProvider)
class IMetadataJournal(Schema):

    userid = TextLine(title=u'User ID', required=True,
                      defaultFactory=get_current_user_id)
    time = Datetime(title=u'Time', required=True,
                    defaultFactory=datetime.now)
    fieldname = TextLine(title=u'Field name')
    added = List(title=u'Added values', value_type=TextLine())
    removed = List(title=u'Removed values', value_type=TextLine())


@provider(IFormFieldProvider)
class IToDoSchema(Schema):

    title = TextLine(title=u'Title', required=True)
    text = RichText(title=u'Text', required=False)
    due_date = Date(title=u'Due date', required=False)
    todolist = TextLine(title=u'Todo List', required=False)


class ToDo(Container):
    implements(IToDo)
