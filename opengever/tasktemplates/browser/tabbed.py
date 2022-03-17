from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.tasktemplates import _
from plone import api


class TaskTemplateFolderTabbedView(TabbedView):
    """Tabbedview for TaskTemplateFolders.
    """

    def __init__(self, context, request):
        """Slap a warning onto the overview of nested tasktemplatefolders as
        they will not be displayed correctly (subtasktemplatefolders do not
        appear in the tasktemplates tab).

        We're asserting on the request not having a form as the tabs themselves,
        which get requested by AJAX, rely on a form in the request data. If
        we'd also slap the portal warning onto those requests, the next 'full'
        page view would display them, as the tabs do not consume a portal
        warning.
        """
        super(TaskTemplateFolderTabbedView, self).__init__(context, request)
        if (self.context.contains_subtasktemplatefolders()
                or self.context.is_subtasktemplatefolder()):
            if not self.request.form:
                msg = _(
                    u'warning_nested_tasktemplatefolder',
                    default=u'Nested TaskTemplateFolders can only be viewed '
                            u'and edited correctly in the new UI.')
                api.portal.show_message(msg, self.request, type='warning')
