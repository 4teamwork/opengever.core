from ftw.upgrade import UpgradeStep
from plone.app.textfield import IRichTextValue
from plone.app.textfield.value import RichTextValue


class UpdateTaskTextFieldToRichText(UpgradeStep):
    """Update task text field to rich text.
    """

    def __call__(self):
        query = {'object_provides': "opengever.task.task.ITask"}
        msg = "Change Task text field from Text field to Richtext field"

        for task in self.objects(query, msg):
            if IRichTextValue.providedBy(task.text):
                continue

            task.text = RichTextValue(
                raw=task.text or "",
                mimeType='text/html',
                outputMimeType='text/x-html-safe',
                encoding='utf-8',
            )
