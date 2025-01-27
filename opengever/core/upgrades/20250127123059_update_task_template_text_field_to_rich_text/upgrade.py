from ftw.upgrade import UpgradeStep
from plone.app.textfield import IRichTextValue
from plone.app.textfield.value import RichTextValue


class UpdateTaskTemplateTextFieldToRichText(UpgradeStep):
    """Update task template text field to rich text.
    """

    def __call__(self):
        query = {'object_provides': "opengever.tasktemplates.content.tasktemplate.ITaskTemplate"}
        msg = "Change task template text field from text field to rich text field"

        for task in self.objects(query, msg):
            if IRichTextValue.providedBy(task.text):
                continue

            task.text = RichTextValue(
                raw=task.text or "",
                mimeType='text/html',
                outputMimeType='text/x-html-safe',
                encoding='utf-8',
            )
