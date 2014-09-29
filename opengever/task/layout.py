from plone.app.layout.globals.layout import LayoutPolicy


class TaskLayoutPolicy(LayoutPolicy):

    def bodyClass(self, template, view):
        """Extends default body class with the subtask class, for subtasks.
        Used for displaying different icons for subtasks.
        """

        body_class = super(TaskLayoutPolicy, self).bodyClass(template, view)

        if self.context.get_is_subtask():
            body_class = '{} subtask'.format(body_class)

        return body_class
