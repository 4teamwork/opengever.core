from plone import api
from plone.app.contentlisting.interfaces import IContentListingObject
from Products.ZCatalog.interfaces import ICatalogBrain
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.globalrequest import getRequest


class DocumentLinkWidget(object):

    template = ViewPageTemplateFile('document_link.pt')

    def __init__(self, document):
        self.document = IContentListingObject(document)
        self.context = self.document
        self.request = getRequest()

    def get_url(self):
        return self.document.getURL()

    def portal_url(self):
        return api.portal.get().absolute_url()

    def get_css_class(self):
        classes = ['document_link']
        if self.show_icon:
            classes.append(self.document.ContentTypeClass())
        if self.context.is_removed:
            classes.append('removed_document')

        return ' '.join(classes)

    def get_title(self):
        if self.title is not None:
            return self.title
        return self.document.Title().decode('utf-8')

    def render(self, title=None, show_icon=True):
        self.title = title
        self.show_icon = show_icon
        return self.template(self, self.request)

    def is_view_allowed(self):
        # Avoid object lookup for catalog brains as catalog searches are
        # security aware anyway.
        if ICatalogBrain.providedBy(self.context.getDataOrigin()):
            return True
        return api.user.has_permission('View', obj=self.context.getObject())
