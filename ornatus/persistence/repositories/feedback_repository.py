import json
import sqlite3

from ornatus.models.feedback import Feedback
from ornatus.persistence.database import Database
from ornatus.persistence.repositories.base import Repository


def _row_to_feedback(row: sqlite3.Row) -> Feedback:
    data = dict(row)
    data["rejected_item_ids"] = json.loads(data["rejected_item_ids"])
    return Feedback(**data)


class FeedbackRepository(Repository[Feedback]):
    def __init__(self, db: Database):
        self._db = db

    def add(self, item: Feedback) -> Feedback:
        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO feedback (
                    id, user_id, recommendation_id, feedback_text,
                    rejected_item_ids, preference_signal, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.id,
                    item.user_id,
                    item.recommendation_id,
                    item.feedback_text,
                    json.dumps(item.rejected_item_ids),
                    item.preference_signal.value,
                    item.created_at.isoformat(),
                ),
            )
        return item

    def get(self, item_id: str) -> Feedback | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM feedback WHERE id = ?", (item_id,))
            row = cur.fetchone()
        return _row_to_feedback(row) if row else None

    def list_for_user(self, user_id: str) -> list[Feedback]:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT * FROM feedback WHERE user_id = ? ORDER BY created_at",
                (user_id,),
            )
            rows = cur.fetchall()
        return [_row_to_feedback(row) for row in rows]
