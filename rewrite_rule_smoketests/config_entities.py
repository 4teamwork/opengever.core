class AdminUnit(object):
    """AdminUnit configuration entity.

    Is able to build its most commonly used URLs, and track whether
    it is a classic GEVER admin unit, or one that is used for a dedicated
    Teamraum setup.

    Must be linked to a cluster before being used.
    """

    def __init__(self, unit_id, is_dedicated_teamraum=False):
        self.unit_id = unit_id
        self.is_dedicated_teamraum = is_dedicated_teamraum

        self.cluster = None

    def __repr__(self):
        return "<AdminUnit '%s'>" % self.unit_id

    @property
    def front_page_url(self):
        """The topmost URL of GEVER deployment.

        Is usually the URL of the AdminUnit, except in the case where we
        have a Teamraum redirect.
        """
        if self.is_dedicated_teamraum:
            return self.url + '/workspaces'
        return self.url

    @property
    def url(self):
        """The AdminUnit's URL.
        """
        if not self.cluster.url_contains_site_id:
            # https://lab.onegovgever.ch
            return self.cluster.url

        # https://dev.onegovgever.ch/fd
        return '/'.join((self.cluster.url, self.unit_id))


class Cluster(object):
    """Cluster configuration entity.

    Represents a GEVER cluster (a bunch of deployments that share the same
    OGDS as well as portal).

    The cluster's primary identifier is its base URL. From this URL, all
    other URLs are derived.
    """

    def __init__(self, url, new_portal=False, gever_ui_is_default=False,
                 admin_units=None, url_contains_site_id=None):
        self.url = url
        self.new_portal = new_portal
        self.gever_ui_is_default = gever_ui_is_default
        self.admin_units = admin_units
        self._url_contains_site_id = url_contains_site_id

        # Link admin units to their containing cluster
        for admin_unit in self.admin_units:
            admin_unit.cluster = self

        self.validate()

    def __repr__(self):
        return "<Cluster '%s'>" % self.url

    def validate(self):
        # We want a homogenous URL style to start building other URLs from
        # in order to get predictable results.
        assert not self.url.endswith('/'), \
            "Cluster URLs must not end with trailing slash."

        assert self.url.startswith('https://'), \
            "Cluster URLs be the https:// URLs"

    @property
    def single_unit_setup(self):
        """Whether this cluster is single-unit setup or not.
        """
        return len(self.admin_units) == 1

    @property
    def url_contains_site_id(self):
        """Whether the admin_unit urls contain the site id or not.
        This is always the case for multi-unit setups, and normally not
        for single-unit setups
        """
        if self._url_contains_site_id is None:
            return not self.single_unit_setup
        else:
            return self._url_contains_site_id

    @property
    def portal_url(self):
        """The base URL to this cluster's portal.
        """
        return '/'.join((self.url, 'portal'))

    @property
    def portal_landingpage_url(self):
        """The portal's landing page URL.

        This differs slightly for the old vs. new portal.
        """
        if self.new_portal:
            # https://dev.teamraum.ch/portal
            return self.portal_url

        # https://dev.onegovgever.ch/portal/landingpage
        return '/'.join((self.portal_url, 'landingpage'))
