from datetime import datetime
from opengever.disposition import _
from opengever.disposition.interfaces import IDisposition
from opengever.disposition.interfaces import IHistoryStorage
from opengever.ogds.base.actor import Actor
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer


class DispositionHistory(object):

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
        description = cls.registry.get(mapping.response_type)
        if not description:
            raise ValueError(
                'No specific entry found for {}'.format(
                    mapping.get('transition')))

        return description(mapping)

    def __init__(self, mapping):
        self.mapping = mapping

    @property
    def transition(self):
        return self.mapping.response_type

    @property
    def transition_label(self):
        return translate(self.mapping.response_type,
                         domain="plone",
                         context=getRequest())

    @property
    def date(self):
        return api.portal.get_localized_time(
            datetime=self.mapping.created, long_format=True)

    def msg(self):
        _('msg_disposition_updated', default=u'Updated by ${user}')
        return self.msg_mapping.get(self.transition)

    @property
    def actor_label(self):
        return Actor.lookup(self.mapping.creator).get_label()

    @property
    def _msg_mapping(self):
        return {'user': Actor.lookup(self.mapping.creator).get_link()}

    def details(self):
        return self.mapping.dossiers


class Added(DispositionHistory):
    transition = 'added'
    css_class = 'add'

    def msg(self):
        return _('msg_disposition_added', default=u'Added by ${user}',
                 mapping=self._msg_mapping)

    @property
    def transition_label(self):
        return translate(
            _('label_disposition_added', default=u'Disposition added'),
            context=getRequest())


DispositionHistory.add_description(Added)


class Edited(DispositionHistory):
    transition = 'edited'
    css_class = 'edit'

    def msg(self):
        return _('msg_disposition_edited',
                 default=u'Edited by ${user}',
                 mapping=self._msg_mapping)

    @property
    def transition_label(self):
        return translate(
            _('label_disposition_edited', default=u'Disposition edited'),
            context=getRequest())

DispositionHistory.add_description(Edited)


class Appraised(DispositionHistory):
    transition = 'disposition-transition-appraise'
    css_class = 'appraise'

    def msg(self):
        return _('msg_disposition_appraised',
                 default=u'Appraisal finalized by ${user}',
                 mapping=self._msg_mapping)

DispositionHistory.add_description(Appraised)


class Disposed(DispositionHistory):
    transition = 'disposition-transition-dispose'
    css_class = 'dispose'

    def msg(self):
        return _('msg_disposition_disposed',
                 default=u'Disposition disposed for the archive by ${user}',
                 mapping=self._msg_mapping)

DispositionHistory.add_description(Disposed)


class Archived(DispositionHistory):
    transition = 'disposition-transition-archive'
    css_class = 'archive'

    def msg(self):
        return _('msg_disposition_archived',
                 default=u'The archiving confirmed by ${user}',
                 mapping=self._msg_mapping)

DispositionHistory.add_description(Archived)


class Closed(DispositionHistory):
    transition = 'disposition-transition-close'
    css_class = 'close'

    def msg(self):
        return _(
            'msg_disposition_close',
            default=u'Disposition closed and all dossiers destroyed by ${user}',
            mapping=self._msg_mapping)

DispositionHistory.add_description(Closed)


class AppraisedToClosed(Closed):
    transition = 'disposition-transition-appraised-to-closed'

DispositionHistory.add_description(AppraisedToClosed)


class Refused(DispositionHistory):
    transition = 'disposition-transition-refuse'
    css_class = 'refuse'

    def msg(self):
        return _(
            'msg_disposition_refuse',
            default=u'Disposition refused by ${user}',
            mapping=self._msg_mapping)

DispositionHistory.add_description(Refused)


@implementer(IHistoryStorage)
@adapter(IDisposition)
class HistoryStorage(object):

    key = 'disposition_history'

    def __init__(self, context):
        self.context = context
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
        entries = [DispositionHistory.get(mapping)
                   for mapping in self._storage]
        entries.reverse()
        return entries
