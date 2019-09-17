from opengever.base.subscribers import ALLOWED_ENDPOINTS
from opengever.testing import FunctionalTestCase
from zope.browsermenu.interfaces import IBrowserSubMenuItem
from zope.publisher.interfaces.browser import IBrowserView


WHITELIST = (
    # These test views are unsecure by design in order to test security:
    'opengever.base.tests.views.unauthorized.PublishingUnauthorized',
    'opengever.base.tests.views.unauthorized.TraversalUnauthorized',

    # The plone-layout view is zope.Public in Plone too and should not
    # disclose sensitive infos.
    'opengever.base.browser.layout.GeverLayoutPolicy',
    'opengever.contact.browser.layout.OrganizationLayoutPolicy',
    'opengever.contact.browser.layout.PersonLayoutPolicy',
    'opengever.document.browser.layout.DocumentishLayoutPolicy',
    'opengever.meeting.browser.layout.CommitteeLayoutPolicy',
    'opengever.task.layout.TaskLayoutPolicy',

    # These views are customizations of Plone views which are public in
    # Plone too.
    'opengever.base.browser.context.WrapperContextState',
    'opengever.base.browser.ploneform_macros.Macros',
    'opengever.base.widgets.GeverRenderWidget',
    'opengever.base.browser.jsvariables.GeverJSVariables',
    'opengever.base.browser.ploneview.GeverPloneView',

    # The bumblebee token is verified in these views:
    'opengever.bumblebee.browser.callback.ReceiveDocumentPDF',
    'opengever.bumblebee.browser.callback.StoreArchivalFile',
    'opengever.meeting.browser.meetings.zipexport_callback.ReceiveZipPdf',

    # Add-form views are special adapters were the permission is stored
    # differently. These views are verified manually:
    'opengever.disposition.browser.form.DispositionAddView',

    # The custom error page needs to be public, since errors may happen
    # during traversal or publish, in both cases security may not yet
    # properly set up
    'opengever.base.browser.errors.ErrorHandlingView',

    # These views are registered for the IInternalOpengeverRequestLayer only
    # and thus are not reachable with a normal request:
    'opengever.meeting.browser.receiveproposaltransition.ReceiveProposalScheduled',
    'opengever.meeting.browser.receiveproposaltransition.ReceiveProposalUnscheduled',
    'opengever.meeting.browser.receiveproposaltransition.ReceiveProposalDecided',
)


class TestViewSecurity(FunctionalTestCase):

    def test_no_public_views(self):
        registrations = list(self.get_public_view_registrations(
            self.portal.getSiteManager()))
        registrations.sort(key=self.get_dottedname)
        msg = ('Views should not be protected only be the public permission,'
               ' or no permission at all. Please use at least the View'
               ' permission for protecting views.'
               '\nFound views with public permission:\n{}').format('\n'.join(
                   map(self.registration_representation_for_assertion,
                       registrations)))
        assert len(registrations) == 0, msg

    def registration_representation_for_assertion(self, reg):
        return '{} in {}'.format(reg.name.rjust(45),
                                 self.get_dottedname(reg))

    def get_public_view_registrations(self, site_manager):
        from opengever.task.response_syncer import BaseResponseSyncerReceiver

        for reg in self.get_adapter_registrations(site_manager):
            if reg.name == '':
                continue

            if reg.name in ALLOWED_ENDPOINTS:
                continue

            if not IBrowserView.implementedBy(reg.factory):
                continue

            if IBrowserSubMenuItem.implementedBy(reg.factory):
                continue

            if self.get_dottedname(reg) in WHITELIST:
                continue

            if len(reg.required) != 2:
                # Only context/request adapters are published.
                continue

            if issubclass(reg.factory, BaseResponseSyncerReceiver):
                # The BaseResponseSyncerReceiver._check_internal_request
                # makes sure that the request is an internal GEVER request.
                # Those requests must be public.
                continue

            permission_role = getattr(reg.factory, '__roles__', None)
            if permission_role is not None:
                continue

            if not self.get_factory(reg).__module__.startswith('opengever.'):
                continue

            yield reg

    def get_adapter_registrations(self, site_manager):
        for reg in site_manager.registeredAdapters():
            yield reg
        for sm in getattr(site_manager, '__bases__', ()):
            for reg in self.get_adapter_registrations(sm):
                yield reg

    def get_factory(self, registration):
        if registration.factory.__module__ == 'Products.Five.metaclass':
            return registration.factory.__bases__[0]
        else:
            return registration.factory

    def get_dottedname(self, registration):
        factory = self.get_factory(registration)
        return '.'.join((factory.__module__, factory.__name__))
