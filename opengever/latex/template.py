from zope.app.pagetemplate.viewpagetemplatefile import PageTemplateFile


class LatexTemplateFile(PageTemplateFile):
    """Latex template file.
    """

    def __call__(self, instance, **keywords):
        data = self._read_file()
        return data % keywords
