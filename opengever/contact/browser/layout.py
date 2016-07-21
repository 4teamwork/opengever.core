from opengever.base.browser.layout import GeverLayoutPolicy


class PersonLayoutPolicy(GeverLayoutPolicy):

    def bodyClass(self, template, view):
        """Replace the portaltype class if the current context is the
        PersonWrapper object."""

        body_class = super(PersonLayoutPolicy, self).bodyClass(template, view)
        return body_class.replace('portaltype-opengever-contact-contactfolder',
                                  'portaltype-opengever-contact-person')


class OrganizationLayoutPolicy(GeverLayoutPolicy):

    def bodyClass(self, template, view):
        """Replace the portaltype class if the current context is the
        OrganizationWrapper object."""

        body_class = super(OrganizationLayoutPolicy, self).bodyClass(
            template, view)

        return body_class.replace('portaltype-opengever-contact-contactfolder',
                                  'portaltype-opengever-contact-organization')
