import sqlite3

from ornatus.models.preferences import LearnedPreference
from ornatus.persistence.database import Database
from ornatus.persistence.repositories.base import Repository


def _row_to_preference(row: sqlite3.Row) -> LearnedPreference:
    data = dict(row)
    data["active"] = bool(data["active"])
    return LearnedPreference(**data)


class PreferenceRepository(Repository[LearnedPreference]):
    def __init__(self, db: Database):
        self._db = db

    def add(self, item: LearnedPreference) -> LearnedPreference:
        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO learned_preferences (
                    id, user_id, type, value, context, reason, source,
                    confidence, active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.id,
                    item.user_id,
                    item.type.value,
                    item.value,
                    item.context,
                    item.reason,
                    item.source,
                    item.confidence,
                    int(item.active),
                    item.created_at.isoformat(),
                    item.updated_at.isoformat(),
                ),
            )
        return item

    def get(self, item_id: str) -> LearnedPreference | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM learned_preferences WHERE id = ?", (item_id,))
            row = cur.fetchone()
        return _row_to_preference(row) if row else None

    def list_for_user(
        self,
        user_id: str,
        context: str | None = None,
        active_only: bool = True,
    ) -> list[LearnedPreference]:
        """All preferences for a user, optionally scoped to a context.

        ``context`` includes context-specific preferences that match it
        *plus* every non-context-specific preference (item/category/general)
        — those apply regardless of occasion, so they're never excluded by
        a context filter.
        """
        query = "SELECT * FROM learned_preferences WHERE user_id = ?"
        params: list = [user_id]
        if active_only:
            query += " AND active = 1"
        query += " ORDER BY created_at"

        with self._db.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
        preferences = [_row_to_preference(row) for row in rows]

        if context is not None:
            context_lower = context.lower()
            preferences = [
                p
                for p in preferences
                if p.context is None or p.context.lower() in context_lower
            ]
        return preferences
