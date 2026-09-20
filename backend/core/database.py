from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()

# This hook ensures SQLite runs fast locally, but ignores PRAGMAs safely on production PostgreSQL
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Detect the connection dialect type dynamically
    dialect_name = getattr(connection_record, "engine", None)
    if dialect_name and hasattr(dialect_name, "name") and dialect_name.name == "sqlite":
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
        except Exception:
            pass
