from plone.dexterity.browser import add


class DispositionAddForm(add.DefaultAddForm):
    portal_type = 'opengever.disposition.disposition'

    def update(self):
        """Insert selected dossier paths into the request.
        """
        paths = self.request.get('paths', [])
        if paths:
            self.request.set('form.widgets.dossiers', paths)

        return super(DispositionAddForm, self).update()


class DispositionAddView(add.DefaultAddView):
    form = DispositionAddForm
