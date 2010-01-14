from Acquisition import aq_parent
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
    object_roles = schema.Set(title=_(u"Object Roles"),
        description=_(u"The local roles to add."),
        required=True,
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.Roles"))

    related_items_roles = schema.Set(title=_(u"Related Items Roles"),
        description=_(u"The local roles to add."),
        required=True,
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.Roles"))

    parent_roles = schema.Set(title=_(u"Parent Roles"),
        description=_(u"The local roles to add."),
        required=True,
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.Roles"))


class AddLocalRolesAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(IAddLocalRolesAction, IRuleElementData)

    object_roles = []
    related_items_roles = []
    parent_roles = []
    element = "ftw.task.actions.AddLocalRoles"

    @property
    def summary(self):
        return _(u"Add local roles for object: ${object_roles}, "\
                  "related items: ${related_items_roles}, "\
                  "parent: ${parent_roles}",
                  mapping=dict(object_roles=", ".join(self.object_roles),
                               related_items_roles=", ".join(self.related_items_roles),
                               parent_roles=", ".join(self.parent_roles)))


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
            
            # set object roles
            roles = self.element.object_roles
            if roles:
                obj.manage_setLocalRoles(user_id, list(roles))
                obj.reindexObjectSecurity()
            
            # set related items roles
            roles = self.element.related_items_roles
            if roles:
                related_items = getattr(obj, 'relatedItems', [])
                for item in related_items:
                    item.to_object.manage_setLocalRoles(user_id, list(roles))
                    item.to_object.reindexObjectSecurity()
            
            # set parent roles
            roles = self.element.parent_roles
            if roles:
                parent = aq_parent(obj)
                parent.manage_setLocalRoles(user_id, list(self.element.parent_roles))
                parent.reindexObjectSecurity()
        
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
