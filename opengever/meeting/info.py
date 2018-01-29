from plone.locking.browser.info import LockInfoViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SablonValidationInfoViewlet(LockInfoViewlet):

    template = ViewPageTemplateFile('browser/templates/sablon_validation_state.pt')
