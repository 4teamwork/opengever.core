# -*- coding: utf-8 -*-
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base.source import SolrObjPathSourceBinder
from opengever.base.stream import TempfileStreamIterator
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.ech0147 import _
from opengever.ech0147 import model
from opengever.ech0147.interfaces import IECH0147Settings
from opengever.journal.handlers import journal_entry_factory
from plone.autoform import directives
from plone.autoform.form import AutoExtensibleForm
from plone.registry.interfaces import IRegistry
from plone.supermodel.model import Schema
from tempfile import TemporaryFile
from z3c.form import button
from z3c.form import form
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zExceptions import NotFound
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile
from zope import schema
from zope.component import getUtility
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class IECH0147ExportFormSchema(Schema):

    recipients = schema.List(
        title=_(u'label_recipients', default=u'Recipient(s)'),
        description=_(u'help_recipients',
                      default=u'Recipients of the message. Enter one recipient'
                              ' per line.'),
        value_type=schema.TextLine(),
        required=False,
    )

    action = schema.Choice(
        title=_(u'label_action', default=u'Action'),
        description=_(u'help_action', default=u''),
        vocabulary=SimpleVocabulary([
            SimpleTerm(1, '1', _(u'term_action_1', default=u'new')),
            SimpleTerm(3, '3', _(u'term_action_3', default=u'revocation')),
            SimpleTerm(4, '4', _(u'term_action_4', default=u'correction')),
            SimpleTerm(5, '5', _(u'term_action_5', default=u'inquiry')),
            SimpleTerm(6, '6', _(u'term_action_6', default=u'response')),
            SimpleTerm(7, '7', _(u'term_action_7', default=u'key exchange')),
            SimpleTerm(10, '10', _(u'term_action_10', default=u'forwarding')),
            SimpleTerm(12, '12', _(u'term_action_12', default=u'reminder')),
        ]),
    )

    subject = schema.TextLine(
        title=_(u'label_subject', default=u'Subject'),
        required=False,
    )

    comment = schema.TextLine(
        title=_(u'label_comment', default=u'Comment'),
        required=False,
    )

    directive = schema.Choice(
        title=_(u'label_directive', default=u'Directive'),
        description=_(u'help_directive', default=u''),
        vocabulary=SimpleVocabulary([
            SimpleTerm(u'process', 'process',
                       _(u'term_directive_process', default=u'process')),
            SimpleTerm(u'external_process', 'external_process',
                       _(u'term_directive_external_process',
                         default=u'external process')),
            SimpleTerm(u'information', 'information',
                       _(u'term_directive_information',
                         default=u'informationrocess')),
            SimpleTerm(u'comment', 'comment',
                       _(u'term_directive_comment', default=u'comment')),
            SimpleTerm(u'approve', 'approve',
                       _(u'term_directive_approve', default=u'approve')),
            SimpleTerm(u'sign', 'sign',
                       _(u'term_directive_sign', default=u'sign')),
            SimpleTerm(u'send', 'send',
                       _(u'term_directive_send', default=u'send')),
            SimpleTerm(u'complete', 'complete',
                       _(u'term_directive_complete', default=u'complete')),
        ]),
        required=False,
    )

    priority = schema.Choice(
        title=_(u'label_priority', default=u'Priority'),
        vocabulary=SimpleVocabulary([
            SimpleTerm(u'undefined', 'undefined',
                       _(u'term_priority_undefined', default=u'undefined')),
            SimpleTerm(u'medium', 'medium',
                       _(u'term_priority_medium', default=u'medium')),
            SimpleTerm(u'high', 'high',
                       _(u'term_priority_high', default=u'high')),
        ]),
    )

    directives.widget(deadline=DatePickerFieldWidget)
    deadline = schema.Date(
        title=_(u'label_deadline', default=u'Deadline'),
        required=False,
    )

    directives.mode(paths='hidden')
    paths = RelationList(
        title=_(u'label_paths', default=u'Paths'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Path",
            source=SolrObjPathSourceBinder(
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
        if data['subject'] is not None:
            message.subjects = [data['subject']]
        if data['comment'] is not None:
            message.comments = [data['comment']]

        if data['directive']:
            directive = model.Directive(data['directive'])
            directive.priority = data['priority']
            directive.deadline = data['deadline']
            message.directive = directive

        journal_entry = _(u'label_exported_as_ech0147',
                          default=u'Exported as eCH-0147 message')
        for obj in objs:
            message.add_object(obj)
            journal_entry_factory(obj, 'eCH-0147 Export', journal_entry)

        header_dom = message.header().toDOM(element_name='eCH-0147T0:header')
        message_dom = message.binding().toDOM()

        tmpfile = TemporaryFile()
        with ZipFile(tmpfile, 'w', ZIP_DEFLATED, True) as zipfile:
            zipfile.writestr(
                'header.xml', header_dom.toprettyxml(encoding='UTF-8'))
            zipfile.writestr(
                'message.xml', message_dom.toprettyxml(encoding='UTF-8'))
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

    def updateActions(self):
        super(ECH0147ExportForm, self).updateActions()
        self.actions['label_export'].addClass("context")

    def update(self):
        self.request.set('disable_border', 1)

        paths = self.request.form.get('paths', [])
        if paths:
            self.request.form.update({'form.widgets.paths': paths})

        return super(ECH0147ExportForm, self).update()

    def render(self):
        if not self.enabled():
            raise NotFound()
        if self.response_body is None:
            return super(ECH0147ExportForm, self).render()
        return self.response_body

    def available(self):
        if not self.enabled():
            return False
        if IDossierMarker.providedBy(self.context):
            return True
        return False

    def enabled(self):
        registry = getUtility(IRegistry)
        ech0147_settings = registry.forInterface(IECH0147Settings, check=False)
        return ech0147_settings.ech0147_export_enabled
