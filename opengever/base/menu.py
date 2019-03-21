from ftw.contentmenu.interfaces import IContentmenuPostFactoryMenu
from ftw.contentmenu.menu import CombinedActionsWorkflowMenu
from opengever.meeting import is_meeting_feature_enabled
from opengever.webactions.interfaces import IWebActionsMenuItemsPreparer
from plone.app.contentmenu.interfaces import IDisplaySubMenuItem
from plone.app.contentmenu.menu import DisplaySubMenuItem
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


def order_factories(context, factories):
    """Orders the entries in the factory menu based on a hardcoded order.
    """

    factories_order = ['Document',
                       'Document with docucomposer',
                       'Document with docugate',
                       'document_with_template',
                       'document_with_oneoffixx_template',
                       'document_from_officeatwork',
                       'Task',
                       'Add task from template',
                       'Mail',
                       'Subdossier',
                       'Participant',
                       'Business Case Dossier',
                       'Dossier with template',
                       'Disposition',
                       ]

    ordered_factories = []
    for factory_title in factories_order:
        try:
            factory = [f for f in factories if f.get(
                'title') == factory_title][0]
            ordered_factories.append(factory)
        except IndexError:
            pass

    remaining_factories = [
        f for f in factories if f.get('title') not in factories_order]

    all_factories = ordered_factories + remaining_factories
    return all_factories


@implementer(IContentmenuPostFactoryMenu)
@adapter(Interface, Interface)
class FilteredPostFactoryMenu(object):
    """Build a customized factory menu by allowing factories to be filtered and
    renamed.

    Concrete filtering / renaming can be implemented by subclasses.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_filtered(self, factory):
        """Allows a subclass to determine whether a factory should be filtered
        (omitted) or not.
        """
        return False

    def rename(self, factory):
        """Lets a subclass rename a factory entry if necessary, and return the
        modified factory.
        """
        return factory

    def __call__(self, factories):
        filtered_factories = []
        for factory in factories:
            factory = self.rename(factory)

            if not self.is_filtered(factory):
                filtered_factories.append(factory)

        return order_factories(self.context, filtered_factories)


@adapter(IPloneSiteRoot, Interface)
class PloneSitePostFactoryMenu(FilteredPostFactoryMenu):

    def is_filtered(self, factory):
        factory_id = factory.get('id')
        if factory_id == u'opengever.meeting.committeecontainer':
            return not is_meeting_feature_enabled()

        return False


class OGCombinedActionsWorkflowMenu(CombinedActionsWorkflowMenu):

    def getWorkflowMenuItems(self, context, request):
        """ftw.contentmenu >= 2.2.2 does no longer protect the workflows
        "Advanced..." action with "Manage portal".
        We therefore just filter it.
        """

        result = (super(OGCombinedActionsWorkflowMenu, self)
                  .getWorkflowMenuItems(context, request))
        result = filter(lambda item: (item.get('extra', {})
                                      .get('id', None) != 'advanced'), result)
        result = result + self.getSQLWorkflowMenuItems(context)
        result = result + self.getWebActionsMenuItems(context, request)
        return result

    def getSQLWorkflowMenuItems(self, context):
        """Return workflow menu items of SQL based workflows.

        Some SQL-based object types have custom workflows.
        If enabled, workflow actions should appear in the actions menu
        like normal Plone workflow actions.
        """
        model = getattr(context, 'model', None)
        workflow = getattr(model, 'workflow', None)
        if not getattr(workflow, 'show_in_actions_menu', False):
            return []

        transition_controller = workflow.transition_controller
        result = []
        for transition in workflow.get_transitions(model.get_state()):
            if not transition.visible or \
               not workflow.can_execute_transition(model, transition.name):
                continue

            result.append({
                'title': transition.title,
                'description': '',
                'action': transition_controller.url_for(
                    context, model, transition.name),
                'selected': False,
                'icon': None,
                'extra': {
                    # JS event handlers register with an ID selector.
                    'id': transition.name,
                    'separator': None,
                    'class': '',
                },
                'submenu': None,
            })

        return result

    def getWebActionsMenuItems(self, context, request):
        """Return webactions action-menu items
        """
        renderer = getMultiAdapter((context, request), IWebActionsMenuItemsPreparer,
                                   name='actions-menu')
        return renderer()


class OGDisplaySubMenuItem(DisplaySubMenuItem):
    """Disable display sub menu item for GEVER in general.
    It should never be possible to change the layout property in the UI.
    """

    implements(IDisplaySubMenuItem)

    def available(self):
        return False
