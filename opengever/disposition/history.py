from datetime import datetime
from five import grok
from opengever.disposition import _
from opengever.disposition.interfaces import IDisposition
from opengever.disposition.interfaces import IHistoryStorage
from opengever.ogds.base.actor import Actor
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone import api
from zope.annotation.interfaces import IAnnotations


class HistoryEntry(object):

    registry = None

    @classmethod
    def add_description(cls, subcls):
        if not cls.registry:
            cls.registry = {}

        if hasattr(subcls, 'transition'):
            cls.registry[subcls.transition] = subcls
        else:
            for transition_id in subcls.transitions:
                cls.registry[transition_id] = subcls

    @classmethod
    def get(cls, mapping):
        description = cls.registry.get(mapping.get('transition'))
        if not description:
            raise ValueError(
                'No specific entry found for {}'.format(
                    mapping.get('transition')))

        return description(mapping)

    def __init__(self, mapping):
        self.mapping = mapping

    @property
    def transition(self):
        return self.mapping.get('transition')

    @property
    def date(self):
        return api.portal.get_localized_time(
            datetime=self.mapping.get('date'), long_format=True)

    def msg(self):
        _('msg_disposition_updated', default=u'Updated by ${user}')
        return self.msg_mapping.get(self.transition)

    @property
    def _msg_mapping(self):
        return {'user': Actor.lookup(self.mapping.get('actor_id')).get_link()}

    def details(self):
        return self.mapping.get('dossiers')


class Added(HistoryEntry):
    transition = 'added'
    css_class = 'add'

    def msg(self):
        return _('msg_disposition_added', default=u'Added by ${user}',
                 mapping=self._msg_mapping)

HistoryEntry.add_description(Added)


class Edited(HistoryEntry):
    transition = 'edited'
    css_class = 'edit'

    def msg(self):
        return _('msg_disposition_edited',
                 default=u'Edited by ${user}',
                 mapping=self._msg_mapping)

HistoryEntry.add_description(Edited)


class Appraised(HistoryEntry):
    transition = 'disposition-transition-appraise'
    css_class = 'appraise'

    def msg(self):
        return _('msg_disposition_appraised',
                 default=u'Appraisal finalized by ${user}',
                 mapping=self._msg_mapping)

HistoryEntry.add_description(Appraised)


class Disposed(HistoryEntry):
    transition = 'disposition-transition-dispose'
    css_class = 'dispose'

    def msg(self):
        return _('msg_disposition_disposed',
                 default=u'Disposition disposed for the archive by ${user}',
                 mapping=self._msg_mapping)

HistoryEntry.add_description(Disposed)


class Archived(HistoryEntry):
    transition = 'disposition-transition-archive'
    css_class = 'archive'

    def msg(self):
        return _('msg_disposition_archived',
                 default=u'The archiving confirmed by ${user}',
                 mapping=self._msg_mapping)

HistoryEntry.add_description(Archived)


class Closed(HistoryEntry):
    transition = 'disposition-transition-close'
    css_class = 'close'

    def msg(self):
        return _(
            'msg_disposition_close',
            default=u'Disposition closed and all dossiers destroyed by ${user}',
            mapping=self._msg_mapping)

HistoryEntry.add_description(Closed)


class HistoryStorage(grok.Adapter):
    grok.provides(IHistoryStorage)
    grok.context(IDisposition)

    key = 'disposition_history'

    def __init__(self, context):
        super(HistoryStorage, self).__init__(context)
        self._annotations = IAnnotations(self.context)
        if self.key not in self._annotations.keys():
            self._annotations[self.key] = PersistentList()

    @property
    def _storage(self):
        return self._annotations[self.key]

    def add(self, transition, actor_id, dossiers):
        """Adds a new history entry to the storage.
        transition: string
        actor_id: user_id as string
        dossiers: a list of dossier representations.
        """

        dossier_list = PersistentList(
            [dossier.get_storage_representation() for dossier in dossiers])
        self._storage.append(
            PersistentDict({'transition': transition,
                            'actor_id': actor_id,
                            'date': datetime.now(),
                            'dossiers': dossier_list}))

    def get_history(self):
        entries = [HistoryEntry.get(mapping) for mapping in self._storage]
        entries.reverse()
        return entries
