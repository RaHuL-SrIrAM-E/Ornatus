"""Deterministic domain logic for clothing creation ("design") — no LLM
reasoning here, same discipline as ``outfit_service``/``preference_service``.

Clothing creation is a distinct concept from outfit recommendation, and the
two must not be confused:

- Outfit recommendation (``ornatus.services.outfit_service``): "I already
  own clothes -> compose an outfit from them." Grounded in real
  ``WardrobeItem`` rows; a recommendation can never reference an item that
  doesn't exist.
- Clothing creation (this module): "I don't have exactly what I want ->
  define a new garment." A ``DesignConcept`` is grounded in a
  ``DesignRequest`` the same way a recommendation is grounded in wardrobe
  items — a concept can't reference a design request that doesn't exist —
  but it does not touch the wardrobe at all. Turning an approved concept
  into a real, ownable item (via visual generation, sourcing/manufacturing,
  purchase, and delivery) is future work, deliberately out of scope here;
  see the module docstring in ``ornatus.models.design`` for where this
  pipeline is headed.

The agent (real or local-deterministic) is responsible for turning a raw
request into a structured ``GarmentSpecification`` — this service only
validates and persists what it's given, exactly like
``ornatus.services.preference_service`` does for preference signals.
"""

from pydantic import ValidationError

from ornatus.models._util import new_id, utc_now
from ornatus.models.design import DesignConcept, DesignRequest, GarmentSpecification
from ornatus.persistence.repositories.design_concept_repository import DesignConceptRepository
from ornatus.persistence.repositories.design_request_repository import DesignRequestRepository


class UnknownDesignRequestError(ValueError):
    def __init__(self, design_request_id: str):
        self.design_request_id = design_request_id
        super().__init__(f"Unknown design request id: {design_request_id}")


def _dedupe(values: list[str]) -> list[str]:
    seen = []
    for value in values:
        cleaned = value.strip()
        if cleaned and cleaned not in seen:
            seen.append(cleaned)
    return seen


class DesignService:
    def __init__(
        self,
        request_repository: DesignRequestRepository,
        concept_repository: DesignConceptRepository,
    ):
        self._requests = request_repository
        self._concepts = concept_repository

    def create_request(
        self,
        user_id: str,
        natural_language_request: str,
        occasion: str | None = None,
        desired_impression: str | None = None,
        budget: float | None = None,
    ) -> DesignRequest:
        now = utc_now()
        request = DesignRequest(
            id=new_id("design"),
            user_id=user_id,
            natural_language_request=natural_language_request,
            occasion=occasion,
            desired_impression=desired_impression,
            budget=budget,
            created_at=now,
            updated_at=now,
        )
        return self._requests.add(request)

    def validate_specification(self, garment_specification: GarmentSpecification | dict) -> GarmentSpecification:
        """Parse/normalize a garment specification. Raises ``ValueError`` if
        it doesn't conform to ``GarmentSpecification`` (e.g. an unrecognized
        ``garment_type``, or a wrong field type) — this is deterministic
        schema validation, not a judgment about whether the design is good.
        """
        if isinstance(garment_specification, GarmentSpecification):
            spec = garment_specification
        else:
            try:
                spec = GarmentSpecification(**garment_specification)
            except ValidationError as exc:
                raise ValueError(f"Invalid garment specification: {exc}") from exc

        return spec.model_copy(
            update={
                "colors": _dedupe(spec.colors),
                "style_tags": _dedupe(spec.style_tags),
            }
        )

    def create_concept(
        self,
        user_id: str,
        design_request_id: str,
        title: str,
        description: str,
        garment_specification: GarmentSpecification | dict,
        rationale: str,
    ) -> DesignConcept:
        if self._requests.get(design_request_id) is None:
            raise UnknownDesignRequestError(design_request_id)

        spec = self.validate_specification(garment_specification)
        concept = DesignConcept(
            id=new_id("concept"),
            design_request_id=design_request_id,
            user_id=user_id,
            title=title,
            description=description,
            garment_specification=spec,
            rationale=rationale,
        )
        return self._concepts.add(concept)

    def get_request(self, design_request_id: str) -> DesignRequest | None:
        return self._requests.get(design_request_id)

    def get_concept(self, concept_id: str) -> DesignConcept | None:
        return self._concepts.get(concept_id)

    def list_requests_for_user(self, user_id: str) -> list[DesignRequest]:
        return self._requests.list_for_user(user_id)

    def list_concepts_for_user(self, user_id: str) -> list[DesignConcept]:
        return self._concepts.list_for_user(user_id)

    def list_concepts_for_request(self, design_request_id: str) -> list[DesignConcept]:
        return self._concepts.list_for_request(design_request_id)

    def get_latest_concept_for_user(self, user_id: str) -> DesignConcept | None:
        return self._concepts.get_latest_for_user(user_id)
