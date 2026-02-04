import opengever.ogds.base  # isort:skip # noqa fix cyclic import
from opengever.exportng.catalog import CommitteePeriodSyncer
from opengever.exportng.catalog import DocumentSyncer
from opengever.exportng.catalog import DossierSyncer
from opengever.exportng.catalog import FileplanEntrySyncer
from opengever.exportng.catalog import SubdossierSyncer
from opengever.exportng.db import create_table
from opengever.exportng.db import engine
from opengever.exportng.db import metadata
from opengever.exportng.journal import JOURNAL_MAPPING
from opengever.exportng.journal import JOURNAL_TABLE
from opengever.exportng.ogds import AgendaItemSyncer
from opengever.exportng.ogds import CommitteeMemberSyncer
from opengever.exportng.ogds import CommitteeSyncer
from opengever.exportng.ogds import GroupSyncer
from opengever.exportng.ogds import MeetingParticipantsSyncer
from opengever.exportng.ogds import MeetingSyncer
from opengever.exportng.ogds import ProposalSyncer
from opengever.exportng.ogds import UserSyncer
from plone import api
from sqlalchemy import delete
from sqlalchemy import or_
from sqlalchemy import select
import logging


logger = logging.getLogger('opengever.exportng')


class Syncer(object):

    def __init__(self, path=None):
        self.query = {}
        if path is not None:
            self.query['path'] = {'query': path, 'depth': -1}

    def create_tables(self):
        create_table(UserSyncer.table, UserSyncer.serializer.mapping)
        create_table(GroupSyncer.table, GroupSyncer.serializer.mapping)
        create_table(JOURNAL_TABLE, JOURNAL_MAPPING)
        create_table(FileplanEntrySyncer.table, FileplanEntrySyncer.serializer.mapping)
        create_table(DossierSyncer.table, DossierSyncer.serializer.mapping)
        create_table(SubdossierSyncer.table, SubdossierSyncer.serializer.mapping)
        create_table(DocumentSyncer.table, DocumentSyncer.serializer.mapping)
        create_table(DocumentSyncer.versions_table, DocumentSyncer.serializer.versions_mapping)
        create_table(CommitteeSyncer.table, CommitteeSyncer.serializer.mapping)
        create_table(CommitteeMemberSyncer.table, CommitteeMemberSyncer.serializer.mapping)
        create_table(MeetingSyncer.table, MeetingSyncer.serializer.mapping)
        create_table(MeetingParticipantsSyncer.table, MeetingParticipantsSyncer.serializer.mapping)
        for tablename, mapping in MeetingSyncer.serializer.additional_mappings.items():
            create_table(tablename, mapping)
        create_table(AgendaItemSyncer.table, AgendaItemSyncer.serializer.mapping)
        for tablename, mapping in AgendaItemSyncer.serializer.additional_mappings.items():
            create_table(tablename, mapping)
        create_table(AgendaItemSyncer.table, AgendaItemSyncer.serializer.mapping)
        create_table(ProposalSyncer.table, ProposalSyncer.serializer.mapping)
        for tablename, mapping in ProposalSyncer.serializer.additional_mappings.items():
            create_table(tablename, mapping)
        create_table(CommitteePeriodSyncer.table, CommitteePeriodSyncer.serializer.mapping)
        metadata.create_all(checkfirst=True)

    def sync(self):
        UserSyncer(engine, metadata).sync()
        GroupSyncer(engine, metadata).sync()
        FileplanEntrySyncer(self.query).sync()
        DossierSyncer(self.query).sync()
        SubdossierSyncer(self.query).sync()
        DocumentSyncer(self.query).sync()
        CommitteePeriodSyncer(self.query).sync()
        CommitteeSyncer(engine, metadata).sync()
        CommitteeMemberSyncer(engine, metadata).sync()
        MeetingSyncer(engine, metadata).sync()
        MeetingParticipantsSyncer(engine, metadata).sync()
        AgendaItemSyncer(engine, metadata).sync()
        ProposalSyncer(engine, metadata).sync()
        self.cleanup_orphans()
        self.validate()

    def cleanup_orphans(self):
        parent_keys = set([])
        for table in [
            FileplanEntrySyncer.table,
            DossierSyncer.table,
            SubdossierSyncer.table,
            AgendaItemSyncer.table,
            MeetingSyncer.table,
            ProposalSyncer.table,
        ]:
            sqltable = metadata.tables[table]
            stmt = select([sqltable.c.objexternalkey])
            with engine.connect() as conn:
                parent_keys.update([r[0] for r in conn.execute(stmt).fetchall()])

        for table in [
            DossierSyncer.table,
            SubdossierSyncer.table,
            DocumentSyncer.table,
        ]:
            sqltable = metadata.tables[table]
            stmt = select([sqltable.c.objexternalkey, sqltable.c.objprimaryrelated])
            with engine.connect() as conn:
                res = conn.execute(stmt).fetchall()
                parents = dict([r for r in res])
            orphans = set(parents.values()) - parent_keys
            if orphans:
                orphan_keys = [k for k, p in parents.items() if p in orphans]
                catalog = api.portal.get_tool('portal_catalog')
                for uid in orphan_keys:
                    res = catalog.unrestrictedSearchResults(UID=uid)
                    logger.info('Orphan object at: %s', res[0].getPath())
                stmt = delete(sqltable).where(sqltable.c.objexternalkey.in_(orphan_keys))
                with engine.connect() as conn:
                    res = conn.execute(stmt)
                    logger.info('Removed %s orphans from table %s.', res.rowcount, table)
                parent_keys -= set(orphan_keys)
                if table == 'documents':
                    versions_table = metadata.tables[DocumentSyncer.versions_table]
                    stmt = delete(versions_table).where(versions_table.c.objexternalkey.in_(orphan_keys))
                    with engine.connect() as conn:
                        res = conn.execute(stmt)
                        logger.info('Removed %s orphans from table %s.', res.rowcount, DocumentSyncer.versions_table)
                journal_table = metadata.tables[JOURNAL_TABLE]
                stmt = delete(journal_table).where(or_(
                    journal_table.c.objexternalkey.in_(orphan_keys),
                    journal_table.c.historyobject.in_(orphan_keys)))
                with engine.connect() as conn:
                    res = conn.execute(stmt)
                    logger.info('Removed %s orphans from table %s.', res.rowcount, JOURNAL_TABLE)

    def validate(self):
        table = metadata.tables[FileplanEntrySyncer.table]
        stmt = select([table.c.objprimaryrelated])
        with engine.connect() as conn:
            fileplanentry_parents = set([r[0] for r in conn.execute(stmt).fetchall()])
        table = metadata.tables[DossierSyncer.table]
        stmt = select([table.c.objprimaryrelated])
        with engine.connect() as conn:
            dossier_parents = set([r[0] for r in conn.execute(stmt).fetchall()])
        invalid_parents = fileplanentry_parents & dossier_parents
        if invalid_parents:
            logger.warning(
                'Fileplan entries and dossiers with common parent: %s',
                list(invalid_parents),
            )
