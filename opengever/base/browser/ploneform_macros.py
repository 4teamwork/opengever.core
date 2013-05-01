from Products.Five.browser import BrowserView

# The ploneform-macros view


class Macros(BrowserView):

    def __getitem__(self, key):
        return self.index.macros[key]
