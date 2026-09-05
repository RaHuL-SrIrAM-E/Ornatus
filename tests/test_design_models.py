import pytest
from pydantic import ValidationError

from ornatus.models.design import DesignConcept, DesignRequest, GarmentSpecification, GarmentType

USER_ID = "user-1"


def test_design_request_requires_natural_language_request():
    with pytest.raises(ValidationError):
        DesignRequest(id="design-1", user_id=USER_ID)


def test_design_request_minimal_construction():
    request = DesignRequest(
        id="design-1",
        user_id=USER_ID,
        natural_language_request="I want a relaxed cream linen shirt for a summer dinner.",
    )

    assert request.occasion is None
    assert request.desired_impression is None
    assert request.budget is None


def test_design_request_only_carries_budget_when_explicitly_given():
    request = DesignRequest(
        id="design-1",
        user_id=USER_ID,
        natural_language_request="A shirt, budget $150.",
        budget=150.0,
    )

    assert request.budget == 150.0


def test_garment_specification_requires_garment_type():
    with pytest.raises(ValidationError):
        GarmentSpecification()


def test_garment_specification_accepts_minimal_fields():
    spec = GarmentSpecification(garment_type=GarmentType.SHIRT)

    assert spec.garment_type == GarmentType.SHIRT
    assert spec.colors == []
    assert spec.style_tags == []
    assert spec.custom_details == {}


def test_garment_specification_rejects_unknown_garment_type():
    with pytest.raises(ValidationError):
        GarmentSpecification(garment_type="spacesuit")


def test_garment_specification_supports_custom_details_extensibility():
    spec = GarmentSpecification(
        garment_type=GarmentType.JACKET,
        custom_details={"closure": "button-front", "pocket_style": "chest pocket"},
    )

    assert spec.custom_details["closure"] == "button-front"


def test_design_concept_requires_garment_specification():
    with pytest.raises(ValidationError):
        DesignConcept(
            id="concept-1",
            design_request_id="design-1",
            user_id=USER_ID,
            title="Relaxed Linen Shirt",
            description="A relaxed shirt.",
            rationale="Matches the request.",
        )


def test_design_concept_references_specification():
    spec = GarmentSpecification(garment_type=GarmentType.SHIRT, material="linen", colors=["cream"])
    concept = DesignConcept(
        id="concept-1",
        design_request_id="design-1",
        user_id=USER_ID,
        title="Relaxed Cream Linen Shirt",
        description="A relaxed cream linen shirt.",
        garment_specification=spec,
        rationale="Matches the request for a relaxed summer shirt.",
    )

    assert concept.garment_specification.material == "linen"
    assert concept.garment_specification.colors == ["cream"]
