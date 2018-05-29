# -*- coding: utf-8 -*-
from ftw.casauth.cas import validate_ticket
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin  # noqa
from zope.interface import alsoProvides

import plone.protect.interfaces


class CASLogin(Service):
    """Handles login and returns a JSON web token (JWT).
    """
    def reply(self):
        data = json_body(self.request)
        if 'ticket' not in data:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='Missing service ticket',
                message='Service ticket must be provided in body.'))

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        uf = getToolByName(self.context, 'acl_users')
        plugins = uf._getOb('plugins')
        authenticators = plugins.listPlugins(IAuthenticationPlugin)
        cas_plugin = None
        jwt_plugin = None
        for id_, authenticator in authenticators:
            if authenticator.meta_type == "CAS Authentication Plugin":
                cas_plugin = authenticator
            elif authenticator.meta_type == "JWT Authentication Plugin":
                jwt_plugin = authenticator

        if cas_plugin is None or jwt_plugin is None:
            self.request.response.setStatus(501)
            return dict(error=dict(
                type='Login failed',
                message='CAS/JWT authentication plugin not installed.'))

        userid = validate_ticket(
            data['ticket'],
            cas_plugin.cas_server_url,
            data['service'],
        )

        user = uf.getUserById(userid)
        payload = {'fullname': user.getProperty('fullname')}
        return {
            'token': jwt_plugin.create_token(userid, data=payload)
        }

    def check_permission(self):
        return
