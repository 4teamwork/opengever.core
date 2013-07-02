from plone.app.layout.globals import layout


class LayoutPolicy(layout.LayoutPolicy):

    def bodyClass(self, template, view):
        """ Get the origin body classes and append the task type.
        """
        body_class = super(LayoutPolicy, self).bodyClass(template, view)
        if self.context.is_subtask():
            body_class += ' tasktype-subtask'
        elif self.context.is_remotetask():
            body_class += ' tasktype-remotetask'
        return body_class
