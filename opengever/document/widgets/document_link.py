from plone import api
from plone.app.contentlisting.interfaces import IContentListingObject
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
        classes = ['document_link', self.document.ContentTypeClass()]
        return ' '.join(classes)

    def get_title(self):
        return self.document.Title().decode('utf-8')

    def render(self):
        return self.template(self, self.request)

    def is_view_allowed(self):
        return api.user.has_permission('View', obj=self.context.getObject())
