from opengever.activity.base import BaseActivity
from opengever.disposition import _
from opengever.disposition.history import DispositionHistory
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_admin_unit
from Products.CMFPlone import PloneMessageFactory


class DispositionAddedActivity(BaseActivity):
    """Activity representation for adding a disposition."""

    @property
    def kind(self):
        return PloneMessageFactory(
            u'disposition-added', default=u'Disposition added')

    @property
    def label(self):
        return self.translate_to_all_languages(
            _('label_disposition_added', u'Disposition added'))

    @property
    def summary(self):
        actor = Actor.lookup(self.context.Creator())
        msg = _('summary_disposition_added',
                u'New disposition added by ${user} on admin unit ${admin_unit}',
                mapping={'user': actor.get_label(with_principal=False),
                         'admin_unit': get_current_admin_unit().label()})
        return self.translate_to_all_languages(msg)

    @property
    def description(self):
        return {}

    def before_recording(self):
        self.context.register_watchers()

    @property
    def actor_id(self):
        return self.context.Creator()


class DispositionStateChangedActivity(BaseActivity):

    def __init__(self, context, request, entry):
        super(DispositionStateChangedActivity, self).__init__(context, request)
        self.entry = entry

    @property
    def kind(self):
        return self.entry.response_type

    @property
    def label(self):
        return self.translate_to_all_languages(
            PloneMessageFactory(self.entry.response_type))

    @property
    def summary(self):
        history = DispositionHistory.get(self.entry)
        return self.translate_to_all_languages(history.msg())

    @property
    def description(self):
        return {}
