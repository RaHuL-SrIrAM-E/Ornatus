import pytest

from ornatus.models.design import GarmentType
from ornatus.services.design_service import UnknownDesignRequestError

USER_ID = "user-1"


def test_create_request_persists_natural_language_request(design_service):
    request = design_service.create_request(
        USER_ID, natural_language_request="I want a relaxed cream linen shirt for a summer dinner."
    )

    assert request.id
    assert request.natural_language_request == "I want a relaxed cream linen shirt for a summer dinner."
    assert design_service.get_request(request.id) == request


def test_create_request_only_sets_budget_when_given(design_service):
    request = design_service.create_request(USER_ID, natural_language_request="A shirt.")
    assert request.budget is None

    with_budget = design_service.create_request(USER_ID, natural_language_request="A shirt.", budget=150.0)
    assert with_budget.budget == 150.0


def test_validate_specification_accepts_a_dict(design_service):
    spec = design_service.validate_specification({"garment_type": "shirt", "material": "linen"})

    assert spec.garment_type == GarmentType.SHIRT
    assert spec.material == "linen"


def test_validate_specification_rejects_unknown_garment_type(design_service):
    with pytest.raises(ValueError):
        design_service.validate_specification({"garment_type": "spacesuit"})


def test_validate_specification_dedupes_colors_and_style_tags(design_service):
    spec = design_service.validate_specification(
        {
            "garment_type": "shirt",
            "colors": ["cream", "cream", " cream "],
            "style_tags": ["relaxed", "relaxed"],
        }
    )

    assert spec.colors == ["cream"]
    assert spec.style_tags == ["relaxed"]


def test_create_concept_requires_a_real_design_request(design_service):
    with pytest.raises(UnknownDesignRequestError):
        design_service.create_concept(
            USER_ID,
            design_request_id="does-not-exist",
            title="Relaxed Cream Linen Shirt",
            description="A relaxed cream linen shirt.",
            garment_specification={"garment_type": "shirt"},
            rationale="n/a",
        )


def test_create_concept_persists_and_links_to_request(design_service):
    request = design_service.create_request(USER_ID, natural_language_request="A relaxed linen shirt.")

    concept = design_service.create_concept(
        USER_ID,
        design_request_id=request.id,
        title="Relaxed Cream Linen Shirt",
        description="A relaxed cream linen shirt, suited for a summer dinner.",
        garment_specification={"garment_type": "shirt", "fit": "relaxed", "colors": ["cream"], "material": "linen"},
        rationale="Matches the request for a relaxed summer shirt.",
    )

    assert concept.design_request_id == request.id
    assert concept.garment_specification.garment_type == GarmentType.SHIRT
    assert design_service.get_concept(concept.id) == concept
    assert design_service.list_concepts_for_request(request.id) == [concept]
    assert design_service.get_latest_concept_for_user(USER_ID) == concept


def test_list_requests_for_user(design_service):
    first = design_service.create_request(USER_ID, natural_language_request="A shirt.")
    second = design_service.create_request(USER_ID, natural_language_request="A jacket.")

    requests = design_service.list_requests_for_user(USER_ID)

    assert [r.id for r in requests] == [first.id, second.id]
