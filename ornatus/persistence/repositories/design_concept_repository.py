import json
import sqlite3

from ornatus.models.design import DesignConcept, GarmentSpecification
from ornatus.persistence.database import Database
from ornatus.persistence.repositories.base import Repository


def _row_to_concept(row: sqlite3.Row) -> DesignConcept:
    data = dict(row)
    data["garment_specification"] = GarmentSpecification(**json.loads(data["garment_specification"]))
    return DesignConcept(**data)


class DesignConceptRepository(Repository[DesignConcept]):
    def __init__(self, db: Database):
        self._db = db

    def add(self, item: DesignConcept) -> DesignConcept:
        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO design_concepts (
                    id, design_request_id, user_id, title, description,
                    garment_specification, rationale, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.id,
                    item.design_request_id,
                    item.user_id,
                    item.title,
                    item.description,
                    item.garment_specification.model_dump_json(),
                    item.rationale,
                    item.created_at.isoformat(),
                ),
            )
        return item

    def get(self, item_id: str) -> DesignConcept | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM design_concepts WHERE id = ?", (item_id,))
            row = cur.fetchone()
        return _row_to_concept(row) if row else None

    def list_for_user(self, user_id: str) -> list[DesignConcept]:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT * FROM design_concepts WHERE user_id = ? ORDER BY created_at",
                (user_id,),
            )
            rows = cur.fetchall()
        return [_row_to_concept(row) for row in rows]

    def list_for_request(self, design_request_id: str) -> list[DesignConcept]:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT * FROM design_concepts WHERE design_request_id = ? ORDER BY created_at",
                (design_request_id,),
            )
            rows = cur.fetchall()
        return [_row_to_concept(row) for row in rows]

    def get_latest_for_user(self, user_id: str) -> DesignConcept | None:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT * FROM design_concepts WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
                (user_id,),
            )
            row = cur.fetchone()
        return _row_to_concept(row) if row else None
