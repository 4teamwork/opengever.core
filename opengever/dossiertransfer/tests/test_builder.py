from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.base.security import elevated_privileges
from opengever.dossier.resolve import LockingResolveManager
from opengever.dossiertransfer.api.schemas import IDossierTransferAPISchema
from opengever.ogds.models.service import ogds_service
from opengever.testing import IntegrationTestCase
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
import json
import pytz


class TestDossierTransferBuilder(IntegrationTestCase):

    features = ('dossier-transfers', )

    @browsing
    def test_builder_creates_valid_transfer(self, browser):
        self.login(self.regular_user, browser=browser)

        now = datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)
        with freeze(now):
            transfer = create(Builder('dossier_transfer'))
            session = create_session()
            session.add(transfer)
            session.flush()

        serialized = getMultiAdapter((transfer, getRequest()), ISerializeToJson)()

        readonly = set(serialized.keys()) - set(IDossierTransferAPISchema.names())
        for field in readonly:
            serialized.pop(field)

        # Can't resolve the dossier in the builder, because builders don't
        # have access to the fixture objects.
        root_dossier = api.content.get(UID=serialized['root'])
        with elevated_privileges():
            LockingResolveManager(root_dossier).resolve()

        with freeze(now):
            browser.open(self.portal, view='@dossier-transfers', method='POST',
                         data=json.dumps(serialized),
                         headers=self.api_headers)

        self.assertEqual(201, browser.status_code)
