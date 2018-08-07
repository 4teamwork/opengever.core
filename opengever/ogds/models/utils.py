from sqlalchemy import MetaData
from sqlalchemy import Table


def alter_column_length(session, tbl_name, col_name, new_length):
    """Helper function to alter an existing SQLAlchemy 'String' column's length,
    depending on the used DB dialect (mysql or oracle).

    Takes an SQLAlchemy session, table name, column name and the new column
    length as arguments.
    """

    engine = session.bind

    # Check if column has already been updated
    meta = MetaData()
    tbl = Table(tbl_name, meta, autoload=True, autoload_with=engine)
    col = [c for c in tbl.columns if c.name == col_name][0]
    if col.type.length == new_length:
        # No upgrade needed
        return

    # Prepare the correct ALTER TABLE statement depending on dialect
    if session.bind.dialect.name == 'mysql':
        statement = "ALTER TABLE `%s` CHANGE COLUMN `%s` `%s` VARCHAR(%s) NOT NULL;" % (
            tbl_name, col_name, col_name, new_length)
    elif session.bind.dialect.name == 'oracle':
        statement = 'ALTER TABLE "%s" MODIFY "%s" VARCHAR2(%sCHAR)' % (
            tbl_name.upper(), col_name.upper(), new_length)
    else:
        return
    session.bind.execute(statement)