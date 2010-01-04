from OFS.SimpleItem import SimpleItem
from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from plone.app.contentrules.browser.formhelper import AddForm, EditForm 
from ftw.task.task import ITask
from ftw.task import _


class IAddLocalRolesAction(Interface):
    """Interface for the configurable aspects of a local roles add action.
    
    This is also used to create add and edit forms, below.
    """

    role_names = schema.Set(title=_(u"Roles"),
                            description=_(u"The local roles to add."),
                            required=True,
                            value_type=schema.Choice(vocabulary="plone.app.vocabularies.Roles"))


class AddLocalRolesAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(IAddLocalRolesAction, IRuleElementData)

    role_names = []
    element = "ftw.task.actions.AddLocalRoles"

    @property
    def summary(self):
        return _(u"Add local roles: ${names}", mapping=dict(names=", ".join(self.role_names)))


class AddLocalRolesActionExecutor(object):
    """The executor for this action.
    
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, IAddLocalRolesAction, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object
        
        if ITask.providedBy(obj):
            user_id = obj.responsible
            roles = self.element.role_names
            for item in obj.relatedItems:
                item.to_object.manage_setLocalRoles(user_id, list(roles))
        
        return True

class AddLocalRolesAddForm(AddForm):
    """An add form for add-local-roles actions.
    """
    form_fields = form.FormFields(IAddLocalRolesAction)
    label = _(u"Add Local Roles Action")
    description = _(u"Add local roles to all related items for the 'responsible' user.")
    form_name = _(u"Configure element")
    
    def create(self, data):
        a = AddLocalRolesAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class AddLocalRolesEditForm(EditForm):
    """An edit form for add-local-roles actions.
    """
    form_fields = form.FormFields(IAddLocalRolesAction)
    label = _(u"Edit Local Roles Action")
    description = _(u"Add local roles to all related items for the 'responsible' user.")
    form_name = _(u"Configure element")
