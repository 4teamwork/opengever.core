# -*- coding: utf-8 -*-
from opengever.base.stream import TempfileStreamIterator
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.ech0147 import _
from opengever.ech0147 import model
from plone.autoform import directives
from plone.autoform.form import AutoExtensibleForm
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.supermodel.model import Schema
from tempfile import TemporaryFile
from z3c.form import button
from z3c.form import form
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile
from zope import schema
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class IECH0147ExportFormSchema(Schema):

    recipients = schema.List(
        title=_('label_recipients', default='Recipients'),
        value_type=schema.TextLine(),
        required=False,
    )

    action = schema.Choice(
        title=_('label_action', default='Action'),
        vocabulary=SimpleVocabulary([
            SimpleTerm(1, '1', 'neu'),
            SimpleTerm(3, '3', 'Widerruf'),
            SimpleTerm(4, '4', 'Korrektur'),
            SimpleTerm(5, '5', 'Anfrage'),
            SimpleTerm(6, '6', 'Antwort'),
            SimpleTerm(7, '7', 'Schlüsselaustausch'),
            SimpleTerm(10, '10', 'Weiterleitung'),
            SimpleTerm(12, '12', 'Mahnung'),
        ])
    )

    directives.mode(paths='hidden')
    paths = RelationList(
        title=_(u'label_paths', default=u'Paths'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Path",
            source=ObjPathSourceBinder(
                object_provides=(
                    'opengever.dossier.behaviors.dossier.IDossierMarker',
                    'opengever.document.behaviors.IBaseDocument'),
                navigation_tree_query={
                    'object_provides':
                    ['opengever.repository.repositoryroot.IRepositoryRoot',
                     'opengever.repository.interfaces.IRepositoryFolder',
                     'opengever.dossier.behaviors.dossier.IDossierMarker'],
                }),
            ),
        required=False,
    )


class ECH0147ExportForm(AutoExtensibleForm, form.Form):
    schema = IECH0147ExportFormSchema
    ignoreContext = True  # don't use context to get widget data
    label = _(u'label_ech0147_export_form', u'eCH 0147 Export')

    response_body = None

    @button.buttonAndHandler(_(u'label_export', default=u'Export'))
    def handleExport(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return

        if data['paths']:
            objs = data['paths']
        else:
            objs = [self.context]

        message = model.MessageT1()
        message.action = data['action']
        message.recipient_id = data['recipients']
        for obj in objs:
            message.add_object(obj)

        header_dom = message.header().toDOM(element_name='eCH-0147T0:header')
        message_dom = message.binding().toDOM()

        tmpfile = TemporaryFile()
        with ZipFile(tmpfile, 'w', ZIP_DEFLATED, True) as zipfile:
            zipfile.writestr('header.xml', header_dom.toprettyxml(encoding='UTF-8'))
            zipfile.writestr('message.xml', message_dom.toprettyxml(encoding='UTF-8'))
            message.add_to_zip(zipfile)

        size = tmpfile.tell()

        response = self.request.response
        response.setHeader(
            "Content-Disposition",
            'inline; filename="message.zip"')
        response.setHeader("Content-type", "application/zip")
        response.setHeader("Content-Length", size)

        self.response_body = TempfileStreamIterator(tmpfile, size)

    @button.buttonAndHandler(_(u'label_cancel', default=u'Cancel'))
    def handleCancel(self, action):
        self.request.response.redirect(self.context.absolute_url())

    def update(self):
        self.request.set('disable_border', 1)

        paths = self.request.form.get('paths', [])
        if paths:
            self.request.form.update({'form.widgets.paths': paths})

        return super(ECH0147ExportForm, self).update()

    def render(self):
        if self.response_body is None:
            return super(ECH0147ExportForm, self).render()
        return self.response_body

    def available(self):
        if IDossierMarker.providedBy(self.context):
            return True
        return False
