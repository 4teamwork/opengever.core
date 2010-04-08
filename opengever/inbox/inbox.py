from five import grok
from opengever.inbox import _
from plone.directives import form
from ftw.table import helper
from opengever.tabbedview import helper as opengever_helper
from opengever.tabbedview.helper import readable_ogds_author
from opengever.tabbedview.browser.tabs import OpengeverSolrListingTab
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

class AssignedTasks(OpengeverSolrListingTab):
    grok.name('tabbedview_view-assigned_tasks')
    columns= (
         ('', helper.draggable),
         ('', helper.path_checkbox),
         ('review_state', 'review_state', helper.translated_string()),
         ('Title', helper.solr_linked),
         {'column' : 'task_type', 
         'column_title' : _(u'label_task_type', 'Task Type')},
         ('deadline', helper.readable_date),
         ('date_of_completion', opengever_helper.readable_date_set_invisibles), # erledigt am
         {'column' : 'responsible', 
         'column_title' : _(u'label_responsible_task', 'Responsible'),  
         'transform' : readable_ogds_author},
         ('issuer', readable_ogds_author), # zugewiesen von
         {'column' : 'created', 
         'column_title' : _(u'label_issued_date', 'issued at'),
         'transform': helper.readable_date },
         )

    def build_query(self):
         group = self.context.inbox_group
         return 'portal_type:ftw.task.task AND responsible:(%s)' % group