"""Clothing-creation ("design") domain models.

This is deliberately a separate concept from outfit recommendation
(``ornatus.models.outfit``): a recommendation composes an outfit from
clothes the user already owns; a design request is what happens when the
user wants something they don't have yet. See the module docstring in
``ornatus.services.design_service`` for the full boundary.

Three models, one pipeline stage each:

- ``DesignRequest`` — the user's original ask, kept close to verbatim
  (``natural_language_request``) plus whatever structured hints were
  explicitly given (occasion, desired impression, budget). This is NOT an
  attempt to fully parse the request — that's what a ``GarmentSpecification``
  is for.
- ``GarmentSpecification`` — the structured clothing requirements derived
  from a request. Deliberately loose: most fields are plain optional
  strings rather than enums, because gap-filling every possible collar/
  sleeve/silhouette vocabulary up front would make this brittle for
  garment types we haven't thought about yet. ``custom_details`` is the
  escape hatch for anything that doesn't fit a named field.
- ``DesignConcept`` — a proposed design, referencing the structured spec
  plus a human-readable rationale. No image/asset fields yet — see the
  class docstring for where those would go later.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from ornatus.models._util import utc_now
from ornatus.models.common import Formality, Season


class GarmentType(StrEnum):
    """The kind of garment being designed. Not the same vocabulary as
    ``ornatus.models.wardrobe.ItemCategory`` on purpose: a wardrobe category
    is a coarse storage/filtering bucket ("top", "bottom"), while a garment
    type here is what's actually being designed ("shirt", "trousers").
    ``OTHER`` plus ``GarmentSpecification.custom_details`` covers anything
    not enumerated yet, so adding a new garment type later doesn't require
    a schema migration.
    """

    SHIRT = "shirt"
    TROUSERS = "trousers"
    DRESS = "dress"
    JACKET = "jacket"
    OUTERWEAR = "outerwear"
    SKIRT = "skirt"
    SWEATER = "sweater"
    ACCESSORY = "accessory"
    OTHER = "other"


class GarmentSpecification(BaseModel):
    """Structured clothing requirements derived from a ``DesignRequest``.

    Deliberately not split into per-garment-type models (``ShirtSpec``,
    ``TrouserSpec``, ...) yet — one flexible shape covers Phase-2's needs,
    and fields that don't apply to a given garment type are simply left
    unset. Revisit only if a garment type needs structured fields no
    amount of ``custom_details`` can reasonably express.
    """

    garment_type: GarmentType
    fit: str | None = None
    silhouette: str | None = None
    colors: list[str] = Field(default_factory=list)
    material: str | None = None
    pattern: str | None = None
    collar: str | None = None
    sleeve: str | None = None
    length: str | None = None
    formality: Formality | None = None
    season: list[Season] = Field(default_factory=list)
    style_tags: list[str] = Field(default_factory=list)
    occasion: str | None = None
    # Free-form escape hatch for anything the named fields above don't
    # cover (e.g. {"closure": "button-front", "pocket_style": "chest
    # pocket"}) — the extensibility point instead of new columns per detail.
    custom_details: dict[str, str] = Field(default_factory=dict)


class DesignRequest(BaseModel):
    """A user's request to create a garment, not just recommend one they
    already own. ``natural_language_request`` is kept verbatim because it's
    the user's actual intent — everything else here is only what was
    explicitly supplied or asked about, not a parse of that text.
    """

    id: str
    user_id: str
    natural_language_request: str
    occasion: str | None = None
    desired_impression: str | None = None
    # Only set when the user explicitly gives a budget — never guessed.
    budget: float | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class DesignConcept(BaseModel):
    """A proposed design for a ``DesignRequest``.

    No image/asset reference yet — once visual generation exists, that's
    an additive field here (e.g. ``image_refs: list[str]``), not a
    reshaping of this model; the same "attach a URL list" pattern already
    used by ``WardrobeItem.image_urls``.
    """

    id: str
    design_request_id: str
    # Denormalized from the owning DesignRequest so concepts can be listed
    # and scoped per-user the same way every other repository does.
    user_id: str
    title: str
    description: str
    garment_specification: GarmentSpecification
    rationale: str
    created_at: datetime = Field(default_factory=utc_now)
