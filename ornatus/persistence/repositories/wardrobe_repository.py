import json
import sqlite3
from datetime import date

from ornatus.models._util import utc_now
from ornatus.models.common import Formality, Season
from ornatus.models.wardrobe import ItemCategory, ItemStatus, WardrobeItem
from ornatus.persistence.database import Database
from ornatus.persistence.repositories.base import Repository

_LIST_FIELDS = ("colors", "season", "suitable_occasions", "style_tags", "image_urls")

_COLUMNS = (
    "id, user_id, name, category, subcategory, colors, pattern, material, brand, "
    "size, fit, formality, season, suitable_occasions, style_tags, image_urls, "
    "purchase_date, purchase_price, source, status, wear_count, last_worn_date, "
    "condition, care_instructions, created_at, updated_at"
)


def _row_to_item(row: sqlite3.Row) -> WardrobeItem:
    data = dict(row)
    for field in _LIST_FIELDS:
        data[field] = json.loads(data[field])
    return WardrobeItem(**data)


def _item_params(item: WardrobeItem) -> tuple:
    return (
        item.id,
        item.user_id,
        item.name,
        item.category.value,
        item.subcategory,
        json.dumps(item.colors),
        item.pattern,
        item.material,
        item.brand,
        item.size,
        item.fit,
        item.formality.value,
        json.dumps([s.value for s in item.season]),
        json.dumps(item.suitable_occasions),
        json.dumps(item.style_tags),
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
    )


class WardrobeRepository(Repository[WardrobeItem]):
    def __init__(self, db: Database):
        self._db = db

    def add(self, item: WardrobeItem) -> WardrobeItem:
        with self._db.cursor() as cur:
            cur.execute(
                f"INSERT INTO wardrobe_items ({_COLUMNS}) "
                f"VALUES ({', '.join('?' * 26)})",
                _item_params(item),
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
        formality: Formality | None = None,
        season: Season | None = None,
        occasion: str | None = None,
    ) -> list[WardrobeItem]:
        query = "SELECT * FROM wardrobe_items WHERE user_id = ?"
        params: list[str] = [user_id]
        if category is not None:
            query += " AND category = ?"
            params.append(category.value)
        if status is not None:
            query += " AND status = ?"
            params.append(status.value)
        if formality is not None:
            query += " AND formality = ?"
            params.append(formality.value)
        query += " ORDER BY id"

        with self._db.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
        items = [_row_to_item(row) for row in rows]

        # season/occasion are stored as JSON lists — filter in Python rather
        # than reaching for SQLite's JSON1 extension for two rarely-used,
        # small-cardinality filters.
        if season is not None:
            items = [i for i in items if season in i.season]
        if occasion is not None:
            occasion_lower = occasion.lower()
            items = [
                i for i in items if any(occasion_lower in o.lower() for o in i.suitable_occasions)
            ]
        return items

    def update(self, item: WardrobeItem) -> WardrobeItem:
        with self._db.cursor() as cur:
            cur.execute(
                """
                UPDATE wardrobe_items SET
                    name = ?, category = ?, subcategory = ?, colors = ?, pattern = ?,
                    material = ?, brand = ?, size = ?, fit = ?, formality = ?, season = ?,
                    suitable_occasions = ?, style_tags = ?, image_urls = ?, purchase_date = ?,
                    purchase_price = ?, source = ?, status = ?, wear_count = ?,
                    last_worn_date = ?, condition = ?, care_instructions = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    item.name,
                    item.category.value,
                    item.subcategory,
                    json.dumps(item.colors),
                    item.pattern,
                    item.material,
                    item.brand,
                    item.size,
                    item.fit,
                    item.formality.value,
                    json.dumps([s.value for s in item.season]),
                    json.dumps(item.suitable_occasions),
                    json.dumps(item.style_tags),
                    json.dumps(item.image_urls),
                    item.purchase_date.isoformat() if item.purchase_date else None,
                    item.purchase_price,
                    item.source,
                    item.status.value,
                    item.wear_count,
                    item.last_worn_date.isoformat() if item.last_worn_date else None,
                    item.condition,
                    item.care_instructions,
                    item.updated_at.isoformat(),
                    item.id,
                ),
            )
        return item

    def mark_worn(self, item_id: str, worn_on: date) -> WardrobeItem | None:
        item = self.get(item_id)
        if item is None:
            return None
        item.wear_count += 1
        item.last_worn_date = worn_on
        item.updated_at = utc_now()
        return self.update(item)
