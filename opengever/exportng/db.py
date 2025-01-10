from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import os


COLUMN_TYPES = {
    'varchar': String,
    'text': Text,
    'jsonb': JSONB,
    'integer': Integer,
    'date': Date,
    'datetime': DateTime,
    'boolean': Boolean,
}

dsn = os.environ.get('EXPORTNG_DSN', 'postgresql:///exportng')

engine = create_engine(dsn)
metadata = MetaData(bind=engine)


def create_table(table, mapping):
    if table in metadata.tables:
        return
    cols = []
    for attr in mapping:
        cols.append(Column(
            attr.col_name,
            COLUMN_TYPES[attr.col_type],
            nullable=True,
        ))
    cols.append(Column('_created_at', DateTime, index=True, server_default=func.now()))
    cols.append(Column('_modified_at', DateTime, index=True, onupdate=func.now()))
    cols.append(Column('_synced_at', DateTime, index=True, onupdate=func.now()))
    cols.append(Column('_deleted', Boolean, index=True, default=False))
    cols.append(Column('_imported_at', DateTime, index=True, nullable=True))
    cols.append(Column('_objaddress', String, index=True, nullable=True))
    Table(table, metadata, *cols)
