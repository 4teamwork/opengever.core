from plone.dexterity.browser.view import DefaultView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class OGDefaultView(DefaultView):
    """A customized default view for Dexterity content.

    Unlike dexterity, we use exactly the same template for items and folderish
    content. It's based on Dexterity's `item.pt` with the addition of checking
    `ommited_fields`.

    On some types we don't necessarily want to show all the fields, so we
    add an `omitted_fields` property that is checked in the slightly customized
    template and allows us to drop specific fields.
    """

    template = ViewPageTemplateFile('templates/content.pt')

    DEFAULT_OMITTED_FIELDS = ['IBasic.description',
                              'description']

    @property
    def omitted_fields(self):
        return OGDefaultView.DEFAULT_OMITTED_FIELDS

    def render(self):
        return self.template()
