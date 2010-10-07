from Products.CMFPlone.utils import getToolByName
from Products.CMFPlone.browser.admin import AddPloneSite
from opengever.ogds.base.interfaces import IClientConfiguration
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class AddOpengeverClient(AddPloneSite):

    # these profiles will be installed automatically
    default_extension_profiles = (
        'plonetheme.classic:default',
        'plonetheme.sunburst:default',
        'opengever.policy.base:default',
        )

    # these profiles will be installed automatically after setting
    # the client id
    additional_opengever_profiles = (
        'opengever.examplecontent:developer',
        'opengever.ogds.base:example',
        )

    default_clients = (('mandant1', 'Mandant 1'),
               ('mandant2', 'Mandant 2'))

    def __call__(self):
        data = AddPloneSite.__call__(self)

        form = self.request.form
        submitted = form.get('form.submitted', False)
        if submitted:
            # the form was submitted, the plone site is set up and ready
            site_id = form.get('site_id', 'Plone')
            site = self.context.get(site_id)

            # set the client id in the registry
            registry = getUtility(IRegistry)
            proxy = registry.forInterface(IClientConfiguration)
            proxy.client_id = site_id.decode('utf-8')

            # import the defaul generic setup profiles if needed
            if form.get('developer', False):
                stool = getToolByName(site, 'portal_setup')
                for profile in self.additional_opengever_profiles:
                    stool.runAllImportStepsFromProfile('profile-%s' % profile)

            # set the site title
            title = [c[1] for c in self.default_clients
                     if c[0] == site_id][0]
            site.manage_changeProperties(title=title)

        return data

    def clients(self):
        yielded_selected = False
        for client_id, title in self.default_clients:
            selected = False
            if not yielded_selected:
                if client_id not in self.context.objectIds():
                    selected = True
                    yielded_selected = True

            used = ''
            if client_id in self.context.objectIds():
                used = '[ALREADY INSTALLED]: '

            yield {
                'value': client_id,
                'label': '%s%s (%s)' % (used, title, client_id),
                'selected': selected}
