import sqlite3

from ornatus.models.design import DesignRequest
from ornatus.persistence.database import Database
from ornatus.persistence.repositories.base import Repository


def _row_to_request(row: sqlite3.Row) -> DesignRequest:
    return DesignRequest(**dict(row))


class DesignRequestRepository(Repository[DesignRequest]):
    def __init__(self, db: Database):
        self._db = db

    def add(self, item: DesignRequest) -> DesignRequest:
        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO design_requests (
                    id, user_id, natural_language_request, occasion,
                    desired_impression, budget, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.id,
                    item.user_id,
                    item.natural_language_request,
                    item.occasion,
                    item.desired_impression,
                    item.budget,
                    item.created_at.isoformat(),
                    item.updated_at.isoformat(),
                ),
            )
        return item

    def get(self, item_id: str) -> DesignRequest | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM design_requests WHERE id = ?", (item_id,))
            row = cur.fetchone()
        return _row_to_request(row) if row else None

    def list_for_user(self, user_id: str) -> list[DesignRequest]:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT * FROM design_requests WHERE user_id = ? ORDER BY created_at",
                (user_id,),
            )
            rows = cur.fetchall()
        return [_row_to_request(row) for row in rows]
