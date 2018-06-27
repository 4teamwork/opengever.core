from opengever.meeting.connector.connector import Connector
from opengever.meeting.connector.connector import ConnectorAction


@Connector.register
class CommentAction(ConnectorAction):
    def execute(self):
        text = self.data.get('text')
        uuid = self.data.get('uuid')
        self.context._comment(text, uuid)


@Connector.register
class SubmitAction(ConnectorAction):
    def execute(self):
        text = self.data.get('text')
        uuid = self.data.get('uuid')
        self.context._submit(text, uuid)
