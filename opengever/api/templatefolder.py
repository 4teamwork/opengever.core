from opengever.api.add import FolderPost
from opengever.api.task import deserialize_responsible
from opengever.api.validation import get_validation_errors
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.source import DossierPathSourceBinder
from opengever.base.source import SolrObjPathSourceBinder
from opengever.contact.ogdsuser import OgdsUserToContactAdapter
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.command import CreateDocumentFromTemplateCommand
from opengever.dossier.dossiertemplate import is_create_dossier_from_template_available
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplate
from opengever.dossier.dossiertemplate.form import CreateDossierContentFromTemplateMixin
from opengever.kub import is_kub_feature_enabled
from opengever.kub.entity import KuBEntity
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.models.service import ogds_service
from opengever.task.task import ITask
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.tasktemplates.sources import TaskResponsibleSourceBinder
from plone import api
from plone.dexterity.interfaces import IDexterityContainer
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.supermodel import model
from z3c.form.field import Fields
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope import schema
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds
from zope.schema.interfaces import ConstraintNotSatisfied
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import RequiredMissing


class DocumentFromTemplatePost(Service):
    """API Endpoint to create a document in a dossier from a template.
    """

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        data = json_body(self.request)

        token = data.get('template')
        if isinstance(token, dict):
            token = token.get('token')

        if not token:
            raise BadRequest('Missing parameter template')

        vocabulary = getUtility(IVocabularyFactory,
                                name='opengever.dossier.DocumentTemplatesVocabulary')
        term = vocabulary(self.context).getTermByToken(token)
        template = term.value

        title = data.get('title')
        if not title:
            raise BadRequest('Missing parameter title')

        recipient_id = data.get('recipient')
        sender_id = data.get('sender')
        participations = data.get('participations', [])
        if (recipient_id or sender_id or participations) and not is_kub_feature_enabled():
            raise BadRequest('recipient, sender and participations '
                             'are only supported when KuB feature is active')
        recipient = self.get_contact_data(recipient_id)
        sender = self.get_contact_data(sender_id)
        participation_data = []
        for participation in participations:
            participants = self.get_contact_data(participation['participant_id'])
            participation_data.append({'participants': participants,
                                       'role': participation['role']})

        command = CreateDocumentFromTemplateCommand(
            self.context, template, title, recipient, sender, participation_data)
        document = command.execute()

        serializer = queryMultiAdapter((document, self.request), ISerializeToJson)
        return serializer()

    def get_contact_data(self, contact_id):
        if contact_id:
            if ActorLookup(contact_id).is_kub_contact():
                return (KuBEntity(contact_id), )
            else:
                ogds_user = ogds_service().find_user(contact_id)
                contact = OgdsUserToContactAdapter(ogds_user)
                data = [ogds_user, contact]
                if contact.addresses:
                    data.append(contact.addresses[0])
                if contact.phonenumbers:
                    data.append(contact.phonenumbers[0])
                if contact.mail_addresses:
                    data.append(contact.mail_addresses[0])
                if contact.urls:
                    data.append(contact.urls[0])
                return tuple(data)
        else:
            return tuple()


class DossierFromTemplatePost(FolderPost, CreateDossierContentFromTemplateMixin):
    """API Endpoint to create a dossier from a template.
    """
    def extract_data(self):
        data = self.request_data
        self.type_ = 'opengever.dossier.businesscasedossier'
        self.id_ = data.get("id", None)
        self.title_ = data.get('title', None)

        token = data.get('template')
        if isinstance(token, dict):
            token = token.get('token')
        if not token:
            raise BadRequest('Missing parameter template')
        vocabulary = getUtility(IVocabularyFactory,
                                name='opengever.dossier.DossierTemplatesVocabulary')
        try:
            self.dossier_template = vocabulary(self.context).getTermByToken(token).value
        except LookupError:
            raise BadRequest("Invalid token '{}'".format(token))
        return data

    def reply(self):
        if not is_create_dossier_from_template_available(self.context):
            raise Unauthorized

        serialized_dossier = super(DossierFromTemplatePost, self).reply()
        self.validate_keywords(self.dossier_template, self.request_data.get('keywords'))
        self.obj.__ac_local_roles_block__ = getattr(
            self.dossier_template, '__ac_local_roles_block__', None)
        RoleAssignmentManager(self.dossier_template).copy_assigments_to(self.obj)
        self.create_dossier_content_from_template(self.obj, self.dossier_template)
        return serialized_dossier

    def validate_keywords(self, dossier_template, keywords_data):
        if dossier_template.restrict_keywords and keywords_data:
            allowed_keywords = IDossierTemplate(dossier_template).keywords
            deserializer = queryMultiAdapter(
                (IDossier['keywords'], self.obj, self.request), IFieldDeserializer)
            keywords = deserializer(keywords_data)
            for keyword in keywords:
                if keyword not in allowed_keywords:
                    raise BadRequest("Keyword '{}' is not allowed".format(keyword))


class ITriggerTaskTemplate(model.Schema):

    tasktemplatefolder = schema.Choice(
        required=True,
        source='opengever.tasktemplates.active_tasktemplatefolders'
    )

    start_immediately = schema.Bool(
        required=True,
        default=True
    )


class ITriggerTaskTemplateSources(model.Schema):

    tasktemplates = RelationList(
        required=True,
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            source=SolrObjPathSourceBinder(
                portal_type=('opengever.tasktemplates.tasktemplate'),
                navigation_tree_query={
                    'object_provides':
                        ['opengever.dossier.templatefolder.interfaces.ITemplateFolder',
                         'opengever.tasktemplates.content.templatefoldersschema.ITaskTemplateFolderSchema',
                         'opengever.tasktemplates.content.tasktemplate.ITaskTemplate',
                         ]
                }
            )
        )
    )

    responsible = schema.Choice(
        source=TaskResponsibleSourceBinder(include_teams=True),
        required=True,
    )

    related_documents = RelationList(
        required=False,
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    'review_state': {'not': 'document-state-shadow'},
                    'object_provides':
                    ['opengever.dossier.behaviors.dossier.IDossierMarker',
                     'opengever.document.document.IDocumentSchema',
                     'opengever.task.task.ITask',
                     'ftw.mail.mail.IMail', ],
                }),
        )
    )


class TriggerTaskTemplatePost(Service):
    """API Endpoint to trigger a task template in a dossier.
    """

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        data = json_body(self.request)

        # pre-process vocabulary token for tasktemplatefolder
        token = data.get('tasktemplatefolder')
        if isinstance(token, dict):
            data['tasktemplatefolder'] = token.get('token')

        # use schema validation for basic fields
        errors = get_validation_errors(data, ITriggerTaskTemplate,
                                       allow_unknown_fields=True)
        if errors:
            raise BadRequest(errors)

        main_task_overrides, errors = self._validate_task_overrides(data)
        if errors:
            raise BadRequest(', '.join(errors))

        # post-process vocabulary based tasktemplatefolder
        tasktemplatefolder = self._get_tasktemplatefolder(
            data['tasktemplatefolder'])

        tasktemplate_data = data.get('tasktemplates', [])
        # process vocabulary based tasktemplates
        tasktemplates, responsibles, errors = self._validate_tasktemplates(
            tasktemplatefolder, tasktemplate_data)
        if errors:
            raise BadRequest(', '.join(errors))

        # process vocabulary based related_documents
        related_documents, invalid_urls = self._validate_related_documents(
            data.get('related_documents', []))
        if invalid_urls:
            raise BadRequest(
                "The following related_documents are invalid: {}".format(
                    ', '.join(invalid_urls)))

        start_immediately = data['start_immediately']

        task = tasktemplatefolder.trigger(
            self.context, tasktemplates, related_documents,
            responsibles, start_immediately,
            main_task_overrides=main_task_overrides
        )

        serializer = queryMultiAdapter((task, self.request), ISerializeToJson)
        result = serializer()
        # the folder serializer uses the current url to display the @id. this
        # wont work as we are using the serializer outside a request to the
        # actual item, we are in the @trigger-task-template service. thus we
        # have to make sure to return the correct id.
        result['@id'] = task.absolute_url()
        return result

    def _validate_task_overrides(self, data):
        task_overrides = {}
        errors = []

        title_deserializer = queryMultiAdapter(
            (ITask["title"], self.context, self.request), IFieldDeserializer)
        text_deserializer = queryMultiAdapter(
            (ITask["text"], self.context, self.request), IFieldDeserializer)
        deadline_deserializer = queryMultiAdapter(
            (ITask["deadline"], self.context, self.request), IFieldDeserializer)

        if "title" in data:
            raw_title = data["title"]
            try:
                title = title_deserializer(raw_title)
            except (RequiredMissing, ConstraintNotSatisfied):
                errors.append(
                    u'Invalid title "{}"'.format(raw_title))
            else:
                task_overrides["title"] = title

        if "text" in data:
            raw_text = data["text"]
            try:
                text = text_deserializer(raw_text)
            except (RequiredMissing, ConstraintNotSatisfied):
                errors.append(
                    u'Invalid text "{}"'.format(raw_text))
            else:
                task_overrides["text"] = text

        if "deadline" in data:
            raw_deadline = data["deadline"]
            try:
                deadline = deadline_deserializer(raw_deadline)
            except (RequiredMissing, ConstraintNotSatisfied):
                errors.append(
                    u'Invalid deadline "{}"'.format(raw_deadline))
            else:
                task_overrides["deadline"] = deadline

        return task_overrides, errors

    def _get_tasktemplatefolder(self, token):
        return api.content.get(UID=token)

    def _validate_tasktemplates(self, tasktemplatefolder, data):
        tasktemplates_field = Fields(
            ITriggerTaskTemplateSources)['tasktemplates'].field
        tasktemplates_deserializer = queryMultiAdapter(
            (tasktemplates_field, self.context, self.request),
            IFieldDeserializer)

        responsible_field = Fields(
            ITriggerTaskTemplateSources)['responsible'].field
        responsible_deserializer = queryMultiAdapter(
            (responsible_field, self.context, self.request),
            IFieldDeserializer)

        tasktemplates = []
        responsibles = {}
        errors = []

        if not data:
            errors.append('At least one tasktemplate is required')

        valid_templates = tasktemplatefolder.objectValues()

        for template_data in data:
            raw_responsible = template_data.pop('responsible', None)

            try:
                template = tasktemplates_deserializer(template_data)[0]
            except (RequiredMissing, ConstraintNotSatisfied):
                errors.append(
                    u'The tasktemplate {} is invalid'.format(template))
            else:
                if template not in valid_templates:
                    errors.append(
                        u'The tasktemplate {} is outside the selected '
                        'template folder'.format(template.absolute_url()))
                else:
                    tasktemplates.append(template)

                # prefill defaults. the users can be interactive but need to
                # be present.
                by_template = {
                    'responsible': template.responsible,
                    'responsible_client': template.responsible_client
                }
                overrides, override_errors = self._validate_task_overrides(
                    template_data
                )
                by_template.update(overrides)
                errors.extend(override_errors)

                responsibles[template.id] = by_template
                if not raw_responsible:
                    continue
                try:
                    responsible = responsible_deserializer(raw_responsible)
                except (RequiredMissing, ConstraintNotSatisfied):
                    errors.append(
                        u'invalid responsible {} for template {}'.format(
                            raw_responsible, template))
                else:
                    by_template['responsible'] = responsible

                    # it seems we need one additional deserialization step
                    # where we remove the client prefix from users but not
                    # from teams and inboxes
                    deserialized = deserialize_responsible(responsible)
                    if deserialized:
                        by_template.update(deserialized)

        return tasktemplates, responsibles, errors

    def _validate_related_documents(self, data):
        field = Fields(
            ITriggerTaskTemplateSources)['related_documents'].field
        deserializer = queryMultiAdapter(
            (field, self.context, self.request), IFieldDeserializer)

        documents = []
        invalid_urls = []

        for doc_url in data:
            try:
                doc = deserializer(doc_url)[0]
            except (RequiredMissing, ConstraintNotSatisfied):
                invalid_urls.append(str(doc_url))
            else:
                documents.append(RelationValue(getUtility(IIntIds).getId(doc)))

        return documents, invalid_urls


class TaskTemplateStructureGet(Service):
    """
    """
    def reply(self):
        return self.recursive_serialize(self.context)

    def recursive_serialize(self, obj):
        result = queryMultiAdapter((obj, self.request), ISerializeToJson)()

        if ITaskTemplate.providedBy(obj):
            result['deadline'] = json_compatible(obj.get_absolute_deadline())
            result['is_private'] = False

        if IDexterityContainer.providedBy(obj):
            items = []

            for child in obj.listFolderContents():
                items.append(self.recursive_serialize(child))

            result['items'] = items
        return result
