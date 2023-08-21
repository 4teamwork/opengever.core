from opengever.bundle.browser.multiuploadwidget import MultiFileUploadField
from opengever.bundle.config.importer import ConfigImporter
from opengever.bundle.importer import BundleImporter
from os.path import join as pjoin
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.supermodel import model
from tempfile import mkdtemp
from z3c.form import button
from z3c.form.form import Form
from zope import schema
from zope.globalrequest import getRequest
import json
import logging
import os
import transaction


log = logging.getLogger('opengever.bundle')
log.setLevel(logging.INFO)


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

    allow_skip_units = schema.Bool(
        title=u'Skip import of existing AdminUnits or OrgUnits',
        description=u'Skip import of units if they already exist',
        default=True,
        required=True)

    create_initial_content = schema.Bool(
        title=u'Create default initial content (if not in bundle)',
        description=u'Create inboxes, template folder and private root if no '
                    u'content for these types is defined in the bundle.',
        default=True,
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
        importer = ConfigImporter(
            config_data,
            allow_skip_units=data['allow_skip_units'])
        result = importer.run(development_mode=data['development_mode'])

        with TempBundleDir() as bundle_dir:
            for filename, uploaded_file in uploaded_files.items():
                bundle_dir.save(uploaded_file, filename)

            bundle_importer = BundleImporter(
                self.context,
                bundle_dir.path,
                disable_ldap=True,
                create_guid_index=True,
                no_intermediate_commits=True,
                possibly_unpatch_collective_indexing=False,
                no_separate_connection_for_sequence_numbers=False,
                skip_report=True,
                create_initial_content=data['create_initial_content'],
            )
            bundle_importer.run()

            log.info("Committing transaction...")
            transaction.get().note(
                "Finished import of OGGBundle %r" % bundle_dir.path)
            transaction.commit()
            log.info("Done.")

        if result is not None:
            self._finished = True
            api.portal.show_message(
                u'Bundle imported.',
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


class TempBundleDir(object):

    def __enter__(self):
        self.path = mkdtemp(prefix='ttw-bundle-', suffix='.oggbundle')
        self.manifest = []
        return self

    def save(self, uploaded_file, filename):
        tmp_filename = pjoin(self.path, filename)
        self.manifest.append(tmp_filename)
        with open(tmp_filename, 'w') as tmp_file:
            tmp_file.write(uploaded_file['data'])

    def __exit__(self, exc_type, exc_value, traceback):
        for file_path in self.manifest:
            os.remove(file_path)
        os.rmdir(self.path)
