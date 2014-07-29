from opengever.base.browser.default_view import OGDefaultView


class DossierDefaultView(OGDefaultView):
    """A customized default view for Dexterity content.

    On dossiers, we don't want to show the `public_trial`
    and `public_trial_statement` fields.
    """

    @property
    def omitted_fields(self):
        fields = super(DossierDefaultView, self).omitted_fields
        fields.extend(['IClassification.public_trial',
                       'IClassification.public_trial_statement'])
        return fields
