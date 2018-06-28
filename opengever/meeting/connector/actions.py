from opengever.meeting.connector.connector import Connector
from opengever.meeting.connector.connector import ConnectorAction


@Connector.register
class CommentAction(ConnectorAction):
    def execute(self):
        text = self.data.get('text')
        self.context._comment(text)


@Connector.register
class SubmitAction(ConnectorAction):
    def execute(self):
        text = self.data.get('text')
        self.context._submit(text)


@Connector.register
class RejectAction(ConnectorAction):
    def execute(self):
        text = self.data.get('text')
        self.context._reject(text)
