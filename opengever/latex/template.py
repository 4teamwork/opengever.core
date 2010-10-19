from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class LatexTemplateFile(ViewPageTemplateFile):
    """Latex template file.
    """

    def __call__(self, instance, **keywords):
        text, type_ = self._read_file()
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        return text % keywords
