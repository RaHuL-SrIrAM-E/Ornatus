import json
import sqlite3

from ornatus.models.decision import AgentDecision
from ornatus.persistence.database import Database
from ornatus.persistence.repositories.base import Repository


def _row_to_decision(row: sqlite3.Row) -> AgentDecision:
    data = dict(row)
    data["tools_used"] = json.loads(data["tools_used"])
    data["selected_item_ids"] = json.loads(data["selected_item_ids"])
    return AgentDecision(**data)


class AgentDecisionRepository(Repository[AgentDecision]):
    def __init__(self, db: Database):
        self._db = db

    def add(self, item: AgentDecision) -> AgentDecision:
        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO agent_decisions (
                    id, user_id, user_request, decision_type, tools_used,
                    selected_item_ids, reasoning_summary, outcome, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.id,
                    item.user_id,
                    item.user_request,
                    item.decision_type.value,
                    json.dumps(item.tools_used),
                    json.dumps(item.selected_item_ids),
                    item.reasoning_summary,
                    item.outcome.value,
                    item.created_at.isoformat(),
                ),
            )
        return item

    def get(self, item_id: str) -> AgentDecision | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM agent_decisions WHERE id = ?", (item_id,))
            row = cur.fetchone()
        return _row_to_decision(row) if row else None

    def list_for_user(self, user_id: str) -> list[AgentDecision]:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT * FROM agent_decisions WHERE user_id = ? ORDER BY created_at",
                (user_id,),
            )
            rows = cur.fetchall()
        return [_row_to_decision(row) for row in rows]
