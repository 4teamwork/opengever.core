from five import grok
from opengever.inbox import _
from plone.directives import form
from opengever.tabbedview.browser.tabs import Tasks, Documents
from zope import schema


class IInbox(form.Schema):
    """ Inbox for OpenGever
    """

    form.fieldset(
        u'common',
        label = _(u'fieldset_common', default=u'Common'),
        fields = [
            u'inbox_group',
            ],
        )

    inbox_group = schema.TextLine(
         title = _(u'label_inbox_group', default=u'Inbox Group'),
         description = _(u'help_inbox_group', default=u''),
         required = False,
         )


class GivenTasks(Tasks):
    grok.name('tabbedview_view-given_tasks')

    types = ['opengever.inbox.forwarding']
    depth = 1


class InboxDocuments(Documents):
    grok.context(IInbox)

    # do not list documents in forwardings
    depth = 1

    @property
    def enabled_actions(self):
        actions = super(InboxDocuments, self).enabled_actions
        actions = [action for action in actions
                   if action not in ('create_task',)]
        actions += ['create_forwarding']
        return  actions

    @property
    def major_actions(self):
        actions = super(InboxDocuments, self).major_actions
        actions = [action for action in actions
                   if action not in ('create_task',)]
        actions += ['create_forwarding']
        return  actions
