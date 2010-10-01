from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.table.interfaces import ITableGenerator
from ftw.table import helper
from datetime import datetime, timedelta
from zope.component import queryUtility
from plone.dexterity.utils import createContentInContainer
from Products.statusmessages.interfaces import IStatusMessage

def path_checkbox(item, value):
    preselected = item.getObject().preselected
    return """
            <input type="checkbox" 
                    class="noborder" 
                    name="paths:list" 
                    id="%s" value="%s" 
                    alt="Select %s" 
                    title="Select %s"
                    %s
                    >""" % (item.id, 
                            item.getPath(),  
                            item.Title, 
                            item.Title,
                            preselected and 'checked="checked"' or None
                            )

class AddForm(BrowserView):
    
    __call__ = ViewPageTemplateFile("form.pt")
    
    steps = {
        'templates': {
            'columns' : (('', helper.path_radiobutton), 'Title' ,'created'),
            'types': ('TaskTemplateFolder',)
        },
        'tasks': {
            'columns' : (('', path_checkbox), 'Title', 'created'),
            'types': ('TaskTemplate',)
        }
    }
    
    def listing(self, show='templates'):
        """returns a listing of either TaskTemplateFolders or TaskTemplates"""
        
        templates = self.context.portal_catalog(Type=self.steps[show]['types'])
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(templates,
                                  self.steps[show]['columns'],
                                  sortable = True,
                                  output='json'
                                  )
                                  
    def create(self, paths):
        """generate the task templates"""
        for path in paths:
            template = self.context.restrictedTraverse(path)
            deadline = datetime.today()+timedelta(template.deadline)
            
            data = dict(title=template.title,
                        issuer=template.issuer,
                        responsible=template.responsible,
                        task_type=template.task_type,
                        text=template.text,
                        deadline=deadline
                        )

            task = createContentInContainer(self.context, 
                                               'opengever.task.task', 
                                               **data)
            task.reindexObject()
                                               
        IStatusMessage(self.request).addStatusMessage("tasks created", 
                                                      type="info")
        return self.request.RESPONSE.redirect(self.context.absolute_url()+'#tasks')