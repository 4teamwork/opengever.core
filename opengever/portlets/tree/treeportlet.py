from AccessControl.unauthorized import Unauthorized
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from zope.interface import implements


class ITreePortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    root_path = schema.TextLine(
        title=u"Root Path",
        description=u"the path to the repositoryroot",
        required=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ITreePortlet)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u""):
    #    self.some_field = some_field

    def __init__(self, root_path):
        self.root_path = root_path

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Tree portlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('treeportlet.pt')

    def header(self):
        current = aq_inner(self.context)
        # Don't travsere to top-level application obj if TreePortlet
        # was added to the Plone Site Root
        if self.root_path() != None:
            portal_url = getToolByName(self.context, 'portal_url')
            current = portal_url.getPortalObject().restrictedTraverse(self.root_path().encode('utf-8'))
            return aq_inner(current).Title()
        elif current.Type() != 'Plone Site':
            return current.Title()
            while current.Type() != 'RepositoryRoot':
                current = current.aq_parent
        return aq_inner(self.context).Title()

    def root_path(self):
        return getattr(self.data, 'root_path', None)

    def context_path(self):
        return '/'.join(self.context.getPhysicalPath())

    @property
    def available(self):
        if self.root_path() != None:
            portal_url = getToolByName(self.context, 'portal_url')
            try:
                portal_url.getPortalObject().restrictedTraverse(self.root_path().encode('utf-8'))
            except KeyError:
                return False
            except Unauthorized:
                return False
        return True

    def navigation_url(self):
        site = getToolByName(self.context, 'portal_url').getPortalObject()
        root = site.restrictedTraverse(self.root_path())
        view = root.restrictedTraverse('navigation.json')
        return view.get_caching_url()


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ITreePortlet)

    def create(self, data):
        return Assignment(**data)


# NOTE: If this portlet does not have any configurable parameters, you
# can use the next AddForm implementation instead of the previous.

# class AddForm(base.NullAddForm):
#     """Portlet add form.
#     """
#     def create(self):
#         return Assignment()


# NOTE: If this portlet does not have any configurable parameters, you
# can remove the EditForm class definition and delete the editview
# attribute from the <plone:portlet /> registration in configure.zcml


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ITreePortlet)
