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


@Connector.register
class RejectAction(ConnectorAction):
    def execute(self):
        text = self.data.get('text')
        self.context._reject(text)


@Connector.register
class ScheduleAction(ConnectorAction):
    def execute(self):
        meeting_id = self.data.get('meeting_id')
        uuid = self.data.get('uuid')
        self.context._schedule(meeting_id, uuid)


@Connector.register
class DecideAction(ConnectorAction):
    def execute(self):
        uuid = self.data.get('uuid')
        self.context._decide(uuid)
        self.context._decide()


@Connector.register
class UpdateSubmittedDocumentAction(ConnectorAction):
    def execute(self):
        document_title = self.data.get('document_title')
        submitted_version = self.data.get('submitted_version')
        uuid = self.data.get('uuid')
        self.context._update_submitted_document(
            document_title, submitted_version, uuid)


@Connector.register
class SubmitDocumentAction(ConnectorAction):
    def execute(self):
        document_title = self.data.get('document_title')
        submitted_version = self.data.get('submitted_version')
        self.context._submit_document(
            document_title, submitted_version)
