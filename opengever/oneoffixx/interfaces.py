from zope import schema
from zope.interface import Interface


class IOneoffixxSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable OneOffixx feature',
        description=u'Whether OneOffixx integration is enabled. '
                    'This feature can only be used if officeconnector is activated',
        default=False)

    baseurl = schema.TextLine(
        title=u'Oneoffixx backend base URL',
        description=u'An URL without a trailing slash to the Oneoffixx backend.',
        default=u'',
        required=False,
    )

    fake_sid = schema.TextLine(
        title=u'A fake SID for testing Oneoffixx with preshared testing SIDs',
        description=u'A preshared SID for testing. Should be empty for production. '
                    u'Takes precedence over fetching an SID from the LDAP.',
        default=u'',
        required=False,
    )

    double_encode_bug = schema.Bool(
        title=u'Whether we double urlencode the grant_type.',
        description=u'There used to be a bug in the Oneoffixx backend where the grant_type needed to be doubly urlencoded. '
                    u'This setting provides a disablable future proofing toggle for that behaviour.',
        default=True,
    )

    cache_timeout = schema.Int(
        title=u'Oneoffixx backend caching timeout in seconds.',
        description=u'Quite many of the backend responses are very slow, so we cache them per user. Defaults to 30 days.',
        default=30 * 24 * 60 * 60,
    )

    scope = schema.TextLine(
        title=u'A scope parameter for API versioning.',
        description=u'This is their OAuth2 grant scope they use for '
                    u'versioning the API.',
        default=u'oo_V1WebApi',
        required=False,
    )
