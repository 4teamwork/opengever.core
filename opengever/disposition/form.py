from five import grok
from plone.directives import dexterity


class DispositionAddForm(dexterity.AddForm):
    grok.name('opengever.disposition.disposition')

    def update(self):
        """Insert selected dossier paths in to the request.
        """
        paths = self.request.get('paths', [])
        if paths:
            self.request.set('form.widgets.dossiers', paths)

        return super(DispositionAddForm, self).update()
