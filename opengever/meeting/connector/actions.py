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


@Connector.register
class ScheduleAction(ConnectorAction):
    def execute(self):
        meeting_id = self.data.get('meeting_id')
        self.context._schedule(meeting_id)


@Connector.register
class DecideAction(ConnectorAction):
    def execute(self):
        self.context._decide()


@Connector.register
class UpdateSubmittedDocumentAction(ConnectorAction):
    def execute(self):
        document_title = self.data.get('document_title')
        submitted_version = self.data.get('submitted_version')
        self.context._update_submitted_document(
            document_title, submitted_version)


@Connector.register
class SubmitDocumentAction(ConnectorAction):
    def execute(self):
        document_title = self.data.get('document_title')
        self.context._submit_document(document_title)
