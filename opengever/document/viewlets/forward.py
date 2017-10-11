from plone.app.layout.viewlets.common import ViewletBase


class ForwardViewlet(ViewletBase):
    """Display the message subject
    """

    def render(self):
        if self.request.get("externaledit", None):
            return '<script language="JavaScript">jq(function(){window.location.href="' + str(
                self.context.absolute_url()) + '/external_edit"})</script>'
        return ''
