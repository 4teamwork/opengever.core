import opengever.ogds.base  # isort:skip # noqa fix cyclic import
from opengever.exportng.catalog import CatalogSyncer
from opengever.exportng.catalog import DocumentSyncer
from opengever.exportng.catalog import DossierSyncer
from opengever.exportng.catalog import FileplanEntrySyncer
from opengever.exportng.catalog import SubdossierSyncer
from opengever.exportng.db import create_table
from opengever.exportng.db import engine
from opengever.exportng.db import metadata
from opengever.exportng.ogds import GroupSyncer
from opengever.exportng.ogds import UserSyncer
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
        create_table(UserSyncer.table, UserSyncer.mapping)
        create_table(GroupSyncer.table, GroupSyncer.mapping)
        create_table(CatalogSyncer.journal_table, CatalogSyncer.journal_mapping)
        create_table(FileplanEntrySyncer.table, FileplanEntrySyncer.mapping)
        create_table(DossierSyncer.table, DossierSyncer.mapping)
        create_table(SubdossierSyncer.table, SubdossierSyncer.mapping)
        create_table(DocumentSyncer.table, DocumentSyncer.mapping)
        create_table(DocumentSyncer.versions_table, DocumentSyncer.versions_mapping)
        metadata.create_all(checkfirst=True)

    def sync(self):
        UserSyncer(engine, metadata).sync()
        GroupSyncer(engine, metadata).sync()
        FileplanEntrySyncer(self.query).sync()
        DossierSyncer(self.query).sync()
        SubdossierSyncer(self.query).sync()
        DocumentSyncer(self.query).sync()
        self.cleanup_orphans()

    def cleanup_orphans(self):
        keys = set([])
        for table in [
            FileplanEntrySyncer.table,
            DossierSyncer.table,
            SubdossierSyncer.table,
        ]:
            sqltable = metadata.tables[table]
            stmt = select([sqltable.c.objexternalkey])
            with engine.connect() as conn:
                keys.update([r[0] for r in conn.execute(stmt).fetchall()])

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
            orphans = set(parents.values()) - keys
            if orphans:
                orphan_keys = [k for k, p in parents.items() if p in orphans]
                logger.info('Orphans: %s', orphan_keys)
                stmt = delete(sqltable).where(sqltable.c.objexternalkey.in_(orphan_keys))
                with engine.connect() as conn:
                    res = conn.execute(stmt)
                    logger.info('Removed %s orphans from table %s.', res.rowcount, table)
                keys -= set(orphan_keys)
                if table == 'documents':
                    versions_table = metadata.tables[DocumentSyncer.versions_table]
                    stmt = delete(versions_table).where(versions_table.c.objexternalkey.in_(orphan_keys))
                    with engine.connect() as conn:
                        res = conn.execute(stmt)
                        logger.info('Removed %s orphans from table %s.', res.rowcount, DocumentSyncer.versions_table)
                journal_table = metadata.tables[CatalogSyncer.journal_table]
                stmt = delete(journal_table).where(or_(
                    journal_table.c.objexternalkey.in_(orphan_keys),
                    journal_table.c.historyobject.in_(orphan_keys)))
                with engine.connect() as conn:
                    res = conn.execute(stmt)
                    logger.info('Removed %s orphans from table %s.', res.rowcount, CatalogSyncer.journal_table)
