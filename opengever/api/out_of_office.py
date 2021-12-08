from datetime import datetime
from opengever.ogds.base.utils import ogds_service
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zExceptions import BadRequest


class OutOfOfficeGet(Service):

    def reply(self):
        userid = api.user.get_current().getId()
        user = ogds_service().fetch_user(userid)
        result = {
            '@id': '{}/@out-of-office'.format(self.context.absolute_url()),
            'absent': user.absent,
            'absent_from': json_compatible(user.absent_from),
            'absent_to': json_compatible(user.absent_to)
        }
        return result


class OutOfOfficePatch(Service):

    def validate_dates(self, absent_from, absent_to):
        if (absent_from or absent_to) is None:
            return
        if (absent_from and absent_to) is None:
            raise BadRequest(u'Either absent_from and absent_to must both be set or neither.')

        if absent_from > absent_to:
            raise BadRequest(u'absent_from date must be before absent_to date.')

    def reply(self):
        data = json_body(self.request)

        userid = api.user.get_current().getId()
        user = ogds_service().fetch_user(userid)

        if 'absent' in data:
            user.absent = data['absent']

        if 'absent_from' in data or 'absent_to' in data:
            if 'absent_from' in data:
                absent_from = data['absent_from']
                if absent_from is not None:
                    absent_from = datetime.strptime(absent_from, '%Y-%m-%d').date()
                user.absent_from = absent_from
            else:
                absent_from = user.absent_from
            if 'absent_to' in data:
                absent_to = data['absent_to']

                if absent_to is not None:
                    absent_to = datetime.strptime(absent_to, '%Y-%m-%d').date()
                user.absent_to = absent_to
            else:
                absent_to = user.absent_to

            self.validate_dates(absent_from, absent_to)

        prefer = self.request.getHeader('Prefer')
        if prefer == 'return=representation':
            self.request.response.setStatus(200)
            return {
                '@id': '{}/@out-of-office'.format(self.context.absolute_url()),
                'absent': user.absent,
                'absent_from': json_compatible(user.absent_from),
                'absent_to': json_compatible(user.absent_to)
            }

        return self.reply_no_content()
