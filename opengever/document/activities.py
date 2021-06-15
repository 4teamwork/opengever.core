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
        return {}
