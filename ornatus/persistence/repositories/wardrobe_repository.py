import json
import sqlite3

from ornatus.models.wardrobe import ItemCategory, ItemStatus, WardrobeItem
from ornatus.persistence.database import Database
from ornatus.persistence.repositories.base import Repository


def _row_to_item(row: sqlite3.Row) -> WardrobeItem:
    data = dict(row)
    for field in ("colors", "tags", "image_urls"):
        data[field] = json.loads(data[field])
    return WardrobeItem(**data)


class WardrobeRepository(Repository[WardrobeItem]):
    def __init__(self, db: Database):
        self._db = db

    def add(self, item: WardrobeItem) -> WardrobeItem:
        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO wardrobe_items (
                    id, user_id, category, subcategory, colors, pattern, fabric,
                    brand, size, fit, tags, image_urls, purchase_date,
                    purchase_price, source, status, wear_count, last_worn_date,
                    condition, care_instructions, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.id,
                    item.user_id,
                    item.category.value,
                    item.subcategory,
                    json.dumps(item.colors),
                    item.pattern,
                    item.fabric,
                    item.brand,
                    item.size,
                    item.fit,
                    json.dumps(item.tags),
                    json.dumps(item.image_urls),
                    item.purchase_date.isoformat() if item.purchase_date else None,
                    item.purchase_price,
                    item.source,
                    item.status.value,
                    item.wear_count,
                    item.last_worn_date.isoformat() if item.last_worn_date else None,
                    item.condition,
                    item.care_instructions,
                    item.created_at.isoformat(),
                    item.updated_at.isoformat(),
                ),
            )
        return item

    def get(self, item_id: str) -> WardrobeItem | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM wardrobe_items WHERE id = ?", (item_id,))
            row = cur.fetchone()
        return _row_to_item(row) if row else None

    def list_for_user(
        self,
        user_id: str,
        category: ItemCategory | None = None,
        status: ItemStatus | None = None,
    ) -> list[WardrobeItem]:
        query = "SELECT * FROM wardrobe_items WHERE user_id = ?"
        params: list[str] = [user_id]
        if category is not None:
            query += " AND category = ?"
            params.append(category.value)
        if status is not None:
            query += " AND status = ?"
            params.append(status.value)

        with self._db.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
        return [_row_to_item(row) for row in rows]
