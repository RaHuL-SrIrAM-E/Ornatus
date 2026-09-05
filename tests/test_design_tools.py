import pytest

from ornatus.tools.design_tools import make_design_tools

USER_ID = "user-1"


def test_create_design_request_tool_persists(design_service):
    create_design_request, *_ = make_design_tools(design_service, USER_ID)

    result = create_design_request(
        natural_language_request="I want a relaxed cream linen shirt for a summer dinner.",
        occasion="summer dinner",
    )

    assert result["id"]
    assert design_service.get_request(result["id"]) is not None
    assert result["occasion"] == "summer dinner"


def test_save_design_concept_tool_persists_and_links(design_service):
    create_design_request, save_design_concept, *_ = make_design_tools(design_service, USER_ID)
    request = create_design_request(natural_language_request="A relaxed linen shirt.")

    concept = save_design_concept(
        design_request_id=request["id"],
        title="Relaxed Cream Linen Shirt",
        description="A relaxed cream linen shirt.",
        rationale="Matches the request.",
        garment_specification={"garment_type": "shirt", "fit": "relaxed", "colors": ["cream"], "material": "linen"},
    )

    assert concept["design_request_id"] == request["id"]
    assert concept["garment_specification"]["garment_type"] == "shirt"
    assert design_service.get_concept(concept["id"]) is not None


def test_save_design_concept_tool_rejects_unknown_request(design_service):
    _, save_design_concept, *_ = make_design_tools(design_service, USER_ID)

    with pytest.raises(ValueError):
        save_design_concept(
            design_request_id="does-not-exist",
            title="Shirt",
            description="A shirt.",
            rationale="n/a",
            garment_specification={"garment_type": "shirt"},
        )


def test_get_design_concept_tool_returns_none_for_missing(design_service):
    _, _, get_design_concept, _ = make_design_tools(design_service, USER_ID)

    assert get_design_concept(concept_id="does-not-exist") is None


def test_list_design_concepts_tool_scopes_to_user_by_default(design_service):
    create_design_request, save_design_concept, _, list_design_concepts = make_design_tools(
        design_service, USER_ID
    )
    request = create_design_request(natural_language_request="A relaxed linen shirt.")
    save_design_concept(
        design_request_id=request["id"],
        title="Relaxed Cream Linen Shirt",
        description="A relaxed cream linen shirt.",
        rationale="Matches the request.",
        garment_specification={"garment_type": "shirt"},
    )

    concepts = list_design_concepts()

    assert len(concepts) == 1
    assert concepts[0]["design_request_id"] == request["id"]


def test_list_design_concepts_tool_scopes_to_request_when_given(design_service):
    create_design_request, save_design_concept, _, list_design_concepts = make_design_tools(
        design_service, USER_ID
    )
    first_request = create_design_request(natural_language_request="A relaxed linen shirt.")
    second_request = create_design_request(natural_language_request="A black jacket.")
    save_design_concept(
        design_request_id=first_request["id"],
        title="Relaxed Cream Linen Shirt",
        description="A relaxed cream linen shirt.",
        rationale="Matches the request.",
        garment_specification={"garment_type": "shirt"},
    )
    save_design_concept(
        design_request_id=second_request["id"],
        title="Black Jacket",
        description="A black jacket.",
        rationale="Matches the request.",
        garment_specification={"garment_type": "jacket"},
    )

    concepts = list_design_concepts(design_request_id=first_request["id"])

    assert len(concepts) == 1
    assert concepts[0]["design_request_id"] == first_request["id"]
