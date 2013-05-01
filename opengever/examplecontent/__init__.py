LDAP_PROFILE = ('4teamwork LDAP', 'opengever.examplecontent:4teamwork-ldap')

POLICIES = ({
        'title': 'Development with examplecontent',
        'base_profile': 'opengever.policy.base:default',
        'additional_profiles': (
            'opengever.setup:default',
            'opengever.examplecontent:developer',),
        'purge_sql': True,
        'import_users': True,
        'language': 'de-ch',
        'clients': (# {
                # 'client_id': 'peter',
                # 'title': 'Peter',
                # 'configsql': False,
                # 'ip_address': '0.0.0.0',
                # 'site_url': 'http://peter:8080',
                # 'public_url': 'http://peter.com',
                # 'group': 'peter_users',
                # 'inbox_group': 'peter_inbox',
                # 'mail_domain': 'peter.com',
                # },
                    ),
        },)
