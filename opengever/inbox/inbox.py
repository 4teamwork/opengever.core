"""Defines some Vies for Inbox"""
from five import grok
from opengever.inbox import _
from plone.directives import form
from opengever.tabbedview.browser.tabs import Tasks, Documents
from opengever.tabbedview.helper import external_edit_link
from zope import schema
from opengever.mail.interfaces import ISendableDocsContainer

class IInbox(form.Schema, ISendableDocsContainer):
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
    """Displays all Given Tasks"""
    grok.name('tabbedview_view-given_tasks')

    types = ['opengever.inbox.forwarding']
    depth = 1

    @property
    def columns(self):
        """Gets the columns wich wich will be displayed
        """
        remove_columns = ['containing_subdossier']
        columns = []

        for col in super(GivenTasks, self).columns:
            if isinstance(col, dict) and \
                    col.get('column') in remove_columns:
                pass  # remove this column

            else:
                columns.append(col)

        return columns

class InboxDocuments(Documents):
    """Lists all Forwardings in this container
    """
    grok.context(IInbox)

    # do not list documents in forwardings
    depth = 1

    @property
    def columns(self):
        """Gets the columns wich wich will be displayed
        """
        remove_columns = ['containing_subdossier']
        columns = []

        for col in super(InboxDocuments, self).columns:
            if isinstance(col, dict) and \
                    col.get('column') in remove_columns:
                pass  # remove this column
            # remove external_edit_link from the columns not used
            elif isinstance(col, tuple) and col[1] == external_edit_link:
                pass # remove this colun
            else:
                columns.append(col)

        return columns

    @property
    def enabled_actions(self):
        """Defines the enabled Actions"""
        actions = super(InboxDocuments, self).enabled_actions
        actions = [action for action in actions
                   if action not in ('create_task',)]
        actions += ['create_forwarding']
        return  actions

    @property
    def major_actions(self):
        """Defines wich actions are major Actions"""
        actions = super(InboxDocuments, self).major_actions
        actions = [action for action in actions
                   if action not in ('create_task',)]
        actions += ['create_forwarding']
        return  actions
