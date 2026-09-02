"""SQLite connection + schema management.

Kept as a thin wrapper so the storage engine can change later without
touching repositories beyond their SQL: repositories depend on ``Database``
for a connection, not on SQLite syntax being hardcoded elsewhere.
"""

import sqlite3
import threading
from contextlib import contextmanager
from importlib import resources
from pathlib import Path


class Database:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self._connection: sqlite3.Connection | None = None
        # Strands runs tool calls on worker threads, not the thread that
        # constructs the agent/database — sqlite3 connections are only
        # usable from the thread that created them unless told otherwise,
        # and aren't safe for concurrent use even then. One connection,
        # shared, guarded by a lock is enough for Phase 1's traffic.
        self._lock = threading.Lock()

    def connect(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self.path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def initialize_schema(self) -> None:
        schema_sql = resources.files("ornatus.persistence").joinpath("schema.sql").read_text()
        self.connect().executescript(schema_sql)
        self.connect().commit()

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    @contextmanager
    def cursor(self):
        with self._lock:
            conn = self.connect()
            cur = conn.cursor()
            try:
                yield cur
                conn.commit()
            finally:
                cur.close()
