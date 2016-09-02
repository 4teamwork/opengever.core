from opengever.base.browser.layout import GeverLayoutPolicy


class ContactLayoutPolicy(GeverLayoutPolicy):

    def bodyClass(self, template, view):
        """Add additional state_class to the body classes.
        """
        body_class = super(ContactLayoutPolicy, self).bodyClass(template, view)
        return ' '.join((body_class, self.get_state_class()))

    def get_state_class(self):
        if self.context.model.is_active:
            return 'state-active'
        else:
            return 'state-inactive'


class PersonLayoutPolicy(ContactLayoutPolicy):

    def bodyClass(self, template, view):
        """Replace the portaltype class if the current context is the
        PersonWrapper object."""

        body_class = super(PersonLayoutPolicy, self).bodyClass(template, view)
        return body_class.replace('portaltype-opengever-contact-contactfolder',
                                  'portaltype-opengever-contact-person')


class OrganizationLayoutPolicy(ContactLayoutPolicy):

    def bodyClass(self, template, view):
        """Replace the portaltype class if the current context is the
        OrganizationWrapper object."""

        body_class = super(OrganizationLayoutPolicy, self).bodyClass(
            template, view)
        return body_class.replace('portaltype-opengever-contact-contactfolder',
                                  'portaltype-opengever-contact-organization')
