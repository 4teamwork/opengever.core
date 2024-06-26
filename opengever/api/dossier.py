from ftw.mail.interfaces import IEmailAddress
from opengever.api.actors import serialize_actor_id_to_json_summary
from opengever.api.deserializer import GeverDeserializeFromJson
from opengever.api.kub import OrganizationContactSyncer
from opengever.api.kub import PersonContactSyncer
from opengever.api.serializer import extend_with_backreferences
from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.behaviors.protect_dossier import IProtectDossier
from opengever.dossier.behaviors.protect_dossier import IProtectDossierMarker
from opengever.dossier.resolve import AfterResolveJobs
from opengever.dossier.utils import get_main_dossier
from opengever.kub import is_kub_feature_enabled
from opengever.kub.client import KuBClient
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IDossierMarker, Interface)
class SerializeDossierToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeDossierToJson, self).__call__(*args, **kwargs)

        # XXX deprecated
        result[u"responsible_fullname"] = self.context.get_responsible_actor(
        ).get_label(with_principal=False)

        result[u'responsible_actor'] = serialize_actor_id_to_json_summary(
            IDossier(self.context).responsible)
        result[u'reference_number'] = self.context.get_reference_number()
        result[u'email'] = IEmailAddress(self.request).get_email_for_object(
            self.context)
        result[u'blocked_local_roles'] = bool(
            getattr(self.context.aq_inner, '__ac_local_roles_block__', False))
        result[u'is_protected'] = IProtectDossier(self.context).is_dossier_protected() \
            if IProtectDossierMarker.providedBy(self.context) else False
        result[u'has_pending_jobs'] = AfterResolveJobs(self.context).after_resolve_jobs_pending
        extend_with_backreferences(
            result, self.context, self.request, 'relatedDossier')

        return result


@implementer(IDeserializeFromJson)
@adapter(IDossierMarker, Interface)
class DeserializeDossierFromJson(GeverDeserializeFromJson):

    def __call__(self, validate_all=False, data=None, create=False):
        if data and data.get('participations'):
            self.add_participations(data.get('participations'))

        return super(DeserializeDossierFromJson, self).__call__(
            validate_all=validate_all, data=data, create=create)()

    def add_participations(self, participations):
        """"Add participations can handle participant_ids or a dict of
        contact_data, in this case it tries to match to an existing contact or
        create a new one."""
        if not is_kub_feature_enabled():
            return

        kub = KuBClient()
        syncers = {
            'person': PersonContactSyncer(kub),
            'organization': OrganizationContactSyncer(kub),
        }

        for participation in participations:
            # skip participation in other formats (dossier-transform).
            if not isinstance(participation, dict):
                continue

            if participation.get('participant_id'):
                # existing participant_id
                participant_id = participation['participant_id']
                roles = participation['roles']

            else:
                # participation is contact_data (contact needs to be found or created)
                roles = participation.pop('roles')
                syncer = syncers.get(participation.pop('type'))
                participant_id = syncer.sync(None, participation)

            IParticipationAware(self.context).add_participation(participant_id, roles)


@implementer(IExpandableElement)
@adapter(Interface, IOpengeverBaseLayer)
class MainDossier(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=True):
        return {
            'main-dossier': self._get_main_dossier_summary()
        }

    def _get_main_dossier_summary(self):
        main_dossier = get_main_dossier(self.context)
        if not main_dossier:
            return None
        return getMultiAdapter(
            (main_dossier, self.request), ISerializeToJsonSummary
        )()
