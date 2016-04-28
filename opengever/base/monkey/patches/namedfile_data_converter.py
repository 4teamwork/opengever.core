from opengever.base.monkey.patching import MonkeyPatch


class PatchNamedfileNamedDataConverter(MonkeyPatch):
    """Monkeypatch for plone.formwidget.namedfile.convert.NamedDataConverter

    This applies the fix that has been merged in
    https://github.com/plone/plone.formwidget.namedfile/pull/9
    which prevents incorrect MIME types when uploading documents with Firefox.

    This monkeypatch should be removed after updating to
    plone.formwidget.namedfile 1.0.11
    """

    def __call__(self):
        from plone.namedfile.interfaces import INamed
        from plone.namedfile.utils import safe_basename
        from ZPublisher.HTTPRequest import FileUpload

        def toFieldValue(self, value):
            if value is None or value == '':
                return self.field.missing_value

            if INamed.providedBy(value):
                return value
            elif isinstance(value, FileUpload):

                filename = safe_basename(value.filename)

                if filename is not None and not isinstance(filename, unicode):
                    # Work-around for
                    # https://bugs.launchpad.net/zope2/+bug/499696
                    filename = filename.decode('utf-8')

                value.seek(0)
                data = value.read()
                if data or filename:
                    return self.field._type(data=data, filename=filename)
                else:
                    return self.field.missing_value

            else:
                return self.field._type(data=str(value))

        from plone.formwidget.namedfile.converter import NamedDataConverter
        self.patch_refs(NamedDataConverter, 'toFieldValue', toFieldValue)
