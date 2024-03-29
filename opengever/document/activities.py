from opengever.activity import ACTIVITY_TRANSLATIONS
from opengever.activity.base import BaseActivity
from opengever.document import _
from opengever.ogds.base.actor import Actor


class DocumentTitleChangedActivity(BaseActivity):
    """Activity representation for changing a document title.
    """
    kind = 'document-title-changed'

    @property
    def summary(self):
        return self.translate_to_all_languages(
            _(u'summary_document_title_changed',
              u'Title changed by ${user}',
              mapping={'user': Actor.lookup(self.actor_id).get_label()}))

    @property
    def label(self):
        return self.translate_to_all_languages(ACTIVITY_TRANSLATIONS[self.kind])

    @property
    def description(self):
        return {}


class DocumentAuthorChangedActivity(BaseActivity):
    """Activity representation for changing a document author.
    """
    kind = 'document-author-changed'

    @property
    def summary(self):
        return self.translate_to_all_languages(
            _(u'summary_document_author_changed',
              u'Author changed by ${user}',
              mapping={'user': Actor.lookup(self.actor_id).get_label()}))

    @property
    def label(self):
        return self.translate_to_all_languages(ACTIVITY_TRANSLATIONS[self.kind])

    @property
    def description(self):
        return {}


class DocumenVersionCreatedActivity(BaseActivity):
    """Activity representation for adding a new document version.
    """
    kind = 'document-version-created'

    def __init__(self, context, request, comment):
        super(DocumenVersionCreatedActivity, self).__init__(context, request)
        self.comment = comment

    @property
    def summary(self):
        return self.translate_to_all_languages(
            _(u'summary_document_version_created',
              u'New document version created by ${user}',
              mapping={'user': Actor.lookup(self.actor_id).get_label()}))

    @property
    def label(self):
        return self.translate_to_all_languages(ACTIVITY_TRANSLATIONS[self.kind])

    @property
    def description(self):
        if self.comment:
            return self.translate_to_all_languages(
                _(u'label_prefixed_journal_comment',
                  default=u'Comment: ${comment}',
                  mapping={'comment': self.comment}))
        else:
            return {}


class DocumentWatcherAddedActivity(BaseActivity):
    """Activity representation for a watcher being added to a document.
    """

    kind = 'document-watcher-added'

    def __init__(self, context, request, watcherid):
        super(DocumentWatcherAddedActivity, self).__init__(context, request)
        self.watcherid = watcherid

    @property
    def summary(self):
        return self.translate_to_all_languages(
            _('summary_document_watcher_added', u'Added as watcher of the document by ${user}',
              mapping={'user': Actor.lookup(self.actor_id).get_link()}))

    @property
    def description(self):
        return {}

    @property
    def label(self):
        msg = _('label_document_watcher_added', u'Added as watcher of the document')
        return self.translate_to_all_languages(msg)

    def add_activity(self):
        return super(DocumentWatcherAddedActivity, self).add_activity(
            notification_recipients=[self.watcherid])
