from opengever.workspace.interfaces import IToDoSettings
from opengever.workspace.interfaces import IWorkspaceMeetingSettings
from opengever.workspace.interfaces import IWorkspaceSettings
from plone import api
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('opengever.workspace')

DEACTIVATE_WORKSPACE_TRANSITION = 'opengever_workspace--TRANSITION--deactivate--active_inactive'

WHITELISTED_TEAMRAUM_GLOBAL_SOURCES = set()

WHITELISTED_TEAMRAUM_PORTAL_TYPES = {
    'ftw.mail.mail',
    'opengever.document.document',
    'opengever.workspace.folder',
    'opengever.workspace.meetingagendaitem',
    'opengever.workspace.root',
    'opengever.workspace.todo',
    'opengever.workspace.todolist',
    'opengever.workspace.workspace',
}

WHITELISTED_TEAMRAUM_VOCABULARIES = {
    'Behaviors',
    'classification_classification_vocabulary',
    'classification_privacy_layer_vocabulary',
    'classification_public_trial_vocabulary',
    'cmf.calendar.AvailableEventTypes',
    'collective.quickupload.fileTypeVocabulary',
    'collective.taskqueue.queues',
    'Fields',
    'ftw.keywordwidget.UnicodeKeywordVocabulary',
    'ftw.usermigration.mapping_sources',
    'ftw.usermigration.post_migration_hooks',
    'ftw.usermigration.pre_migration_hooks',
    'Interfaces',
    'lifecycle_archival_value_vocabulary',
    'lifecycle_custody_period_vocabulary',
    'lifecycle_retention_period_vocabulary',
    'opengever.base.ReferenceFormatterVocabulary',
    'opengever.document.document_types',
    'opengever.journal.manual_entry_categories',
    'opengever.propertysheets.PropertySheetAssignmentsVocabulary',
    'opengever.workspace.PossibleWorkspaceFolderParticipantsVocabulary',
    'opengever.workspace.RolesVocabulary',
    'opengever.workspace.WorkspaceContentMembersVocabulary',
    'plone.app.content.ValidAddableTypes',
    'plone.app.controlpanel.WickedPortalTypes',
    'plone.app.discussion.vocabularies.CaptchaVocabulary',
    'plone.app.discussion.vocabularies.TextTransformVocabulary',
    'plone.app.vocabularies.Actions',
    'plone.app.vocabularies.AllowableContentTypes',
    'plone.app.vocabularies.AllowedContentTypes',
    'plone.app.vocabularies.AvailableContentLanguages',
    'plone.app.vocabularies.AvailableEditors',
    'plone.app.vocabularies.Catalog',
    'plone.app.vocabularies.CommonTimezones',
    'plone.app.vocabularies.ImagesScales',
    'plone.app.vocabularies.Month',
    'plone.app.vocabularies.MonthAbbr',
    'plone.app.vocabularies.PortalTypes',
    'plone.app.vocabularies.ReallyUserFriendlyTypes',
    'plone.app.vocabularies.Roles',
    'plone.app.vocabularies.Skins',
    'plone.app.vocabularies.SupportedContentLanguages',
    'plone.app.vocabularies.SyndicatableFeedItems',
    'plone.app.vocabularies.SyndicationFeedTypes',
    'plone.app.vocabularies.Timezones',
    'plone.app.vocabularies.UserFriendlyTypes',
    'plone.app.vocabularies.Weekdays',
    'plone.app.vocabularies.WeekdaysAbbr',
    'plone.app.vocabularies.WeekdaysShort',
    'plone.app.vocabularies.Workflows',
    'plone.app.vocabularies.WorkflowStates',
    'plone.app.vocabularies.WorkflowTransitions',
    'plone.contentrules.events',
    'plone.formwidget.relations.cmfcontentsearch',
    'plone.schemaeditor.VocabulariesVocabulary',
    'wicked.vocabularies.BaseConfigurationsOptions',
    'wicked.vocabularies.CacheConfigurationsOptions',
}


def is_workspace_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IWorkspaceSettings)


def is_invitation_feature_enabled():
    return api.portal.get_registry_record(
        'is_invitation_feature_enabled', interface=IWorkspaceSettings)


def is_workspace_meeting_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IWorkspaceMeetingSettings)


def is_todo_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IToDoSettings)
