from opengever.bundle.browser.multiuploadwidget import MultiFileUploadField
from opengever.bundle.config.importer import ConfigImporter
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.supermodel import model
from z3c.form import button
from z3c.form.form import Form
from zope import schema
from zope.globalrequest import getRequest
import json
import os


class IImportBundleSchema(model.Schema):

    development_mode = schema.Bool(
        title=u'Development Mode',
        description=u'Development Mode',
        defaultFactory=lambda: bool(os.environ.get('IS_DEVELOPMENT_MODE')),
        required=True)

    bundle_files = MultiFileUploadField(
        title=u'Bundle files',
        description=u'Select JSON files from OGGBundle to import (e.g. configuration.json)',
        required=True)


class ImportBundleForm(AutoExtensibleForm, Form):

    schema = IImportBundleSchema

    ignoreContext = True
    _finished = False

    @button.buttonAndHandler(u'Import', name='save')
    def handle_import(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # TODO: Reject multiple files with same name
        uploaded_files = {}
        for upload in data['bundle_files']:
            uploaded_files[upload['filename']] = upload

        config_data = json.loads(uploaded_files['configuration.json']['data'])
        importer = ConfigImporter(config_data)
        result = importer.run(development_mode=data['development_mode'])

        if result is not None:
            self._finished = True
            api.portal.show_message(
                u'Units and registry settings imported.',
                request=getRequest(), type='info')

    @button.buttonAndHandler(u'Cancel', name='cancel')
    def handle_cancel(self, action):
        return self.request.response.redirect(self.next_url())

    def next_url(self):
        return self.context.absolute_url()

    def render(self):
        self.request.set('disable_border', True)
        if self._finished:
            return self.request.response.redirect(self.next_url())

        return self.index()
