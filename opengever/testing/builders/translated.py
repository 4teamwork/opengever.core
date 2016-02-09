from opengever.base.behaviors.translated_title import TranslatedTitle


class TranslatedTitleBuilderMixin(object):
    """Set translated title attributes 'correctly' during tests.

    Since there most likely is no preferred language we use the hardcoded
    fallback language.

    This mixin allows us to ignore the attribute-based implementation during
    tests when just 'a title' is required.

    """
    title_fieldname = 'title_{}'.format(TranslatedTitle.FALLBACK_LANGUAGE)

    def titled(self, title):
        if not isinstance(title, unicode):
            title = title.decode('utf-8')

        self.arguments[self.title_fieldname] = title
        return self

    def before_create(self):
        if 'title' in self.arguments:
            self.arguments[self.title_fieldname] = self.arguments.pop('title')
        super(TranslatedTitleBuilderMixin, self).before_create()
