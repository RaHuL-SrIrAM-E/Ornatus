import json
import sqlite3

from ornatus.models.outfit import OutfitRecommendation
from ornatus.persistence.database import Database
from ornatus.persistence.repositories.base import Repository


def _row_to_recommendation(row: sqlite3.Row) -> OutfitRecommendation:
    data = dict(row)
    data["item_ids"] = json.loads(data["item_ids"])
    data["excluded_item_ids"] = json.loads(data["excluded_item_ids"])
    data["preferences_considered"] = json.loads(data["preferences_considered"])
    return OutfitRecommendation(**data)


class OutfitRecommendationRepository(Repository[OutfitRecommendation]):
    def __init__(self, db: Database):
        self._db = db

    def add(self, item: OutfitRecommendation) -> OutfitRecommendation:
        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO outfit_recommendations (
                    id, user_id, request_text, event_reference, weather_summary,
                    item_ids, reasoning, confidence, excluded_item_ids,
                    preferences_considered, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.id,
                    item.user_id,
                    item.request_text,
                    item.event_reference,
                    item.weather_summary,
                    json.dumps(item.item_ids),
                    item.reasoning,
                    item.confidence,
                    json.dumps(item.excluded_item_ids),
                    json.dumps(item.preferences_considered),
                    item.created_at.isoformat(),
                ),
            )
        return item

    def get(self, item_id: str) -> OutfitRecommendation | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM outfit_recommendations WHERE id = ?", (item_id,))
            row = cur.fetchone()
        return _row_to_recommendation(row) if row else None

    def list_for_user(self, user_id: str) -> list[OutfitRecommendation]:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT * FROM outfit_recommendations WHERE user_id = ? ORDER BY created_at",
                (user_id,),
            )
            rows = cur.fetchall()
        return [_row_to_recommendation(row) for row in rows]

    def get_latest_for_user(self, user_id: str) -> OutfitRecommendation | None:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT * FROM outfit_recommendations WHERE user_id = ? "
                "ORDER BY created_at DESC LIMIT 1",
                (user_id,),
            )
            row = cur.fetchone()
        return _row_to_recommendation(row) if row else None
