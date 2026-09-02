"""Preference models.

Two distinct things live here, deliberately not merged:

- ``Preferences`` — a single-row-per-user aggregate style profile
  (preferred colors, brands, a rolled-up ``learned_weights`` map). This was
  scaffolded in Phase 1 as a future target for periodically-distilled
  preferences, but has no repository yet and nothing writes to it.
- ``LearnedPreference`` — the atomic signal Ornatus actually records today,
  one row per learned fact ("dislikes item X", "dislikes wearing blazers to
  client dinners"), each traceable back to the feedback it came from. This
  is what ``get_user_preferences`` reads and what a future distillation
  step would roll up into ``Preferences``.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from ornatus.models._util import utc_now


class Preferences(BaseModel):
    user_id: str
    style_keywords: list[str] = Field(default_factory=list)
    preferred_colors: list[str] = Field(default_factory=list)
    avoided_colors: list[str] = Field(default_factory=list)
    avoided_materials: list[str] = Field(default_factory=list)
    preferred_brands: list[str] = Field(default_factory=list)
    avoided_brands: list[str] = Field(default_factory=list)
    fit_preferences: list[str] = Field(default_factory=list)
    price_sensitivity: str = "moderate"  # "low" | "moderate" | "high"
    # Learned signal weights, updated from wear/feedback/return history.
    # Simple tag -> weight map for now; not a model, deliberately.
    learned_weights: dict[str, float] = Field(default_factory=dict)


class PreferenceType(StrEnum):
    """What a ``LearnedPreference`` is about and its scope — deliberately
    kept as one flat enum rather than separate scope/polarity fields, so a
    caller can't construct a nonsensical combination (there's no
    "item-scoped, no polarity" state to represent).

    Scope narrows from ITEM (one wardrobe item) -> CONTEXT (a category, but
    only for a specific occasion) -> CATEGORY (a category, generally) ->
    GENERAL (a broad style descriptor, not tied to any item or category).
    A rejection should only ever produce the narrowest scope the feedback
    actually supports — see ``ornatus.services.feedback_service``.
    """

    ITEM_DISLIKE = "item_dislike"
    ITEM_LIKE = "item_like"
    CATEGORY_DISLIKE = "category_dislike"
    CATEGORY_LIKE = "category_like"
    CONTEXT_DISLIKE = "context_dislike"
    CONTEXT_LIKE = "context_like"
    GENERAL = "general"


class LearnedPreference(BaseModel):
    id: str
    user_id: str
    type: PreferenceType
    # What the preference is about: a wardrobe item id for ITEM_*, a
    # category/subcategory/style-tag string for CATEGORY_*/CONTEXT_*, or a
    # free descriptor (e.g. "formal") for GENERAL.
    value: str
    # Only meaningful for CONTEXT_* — the occasion this applies to (e.g.
    # "client dinner"). Ignored otherwise.
    context: str | None = None
    # Short, human-readable rationale — typically the feedback text (or an
    # excerpt of it) this signal was derived from.
    reason: str | None = None
    source: str = "feedback"  # "feedback" | "manual" | (future) "wear_history"
    confidence: float = 1.0
    active: bool = True
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
