from five import grok
from opengever.document.document import IDocumentSchema
from plone.stagingbehavior.browser import info
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class BaselineInfoViewlet(info.BaselineInfoViewlet):
    grok.context(IDocumentSchema)
    template = ViewPageTemplateFile('info_baseline.pt')
    
class CheckoutInfoViewlet(info.CheckoutInfoViewlet):
    grok.context(IDocumentSchema)
    template = ViewPageTemplateFile('info_checkout.pt')
    