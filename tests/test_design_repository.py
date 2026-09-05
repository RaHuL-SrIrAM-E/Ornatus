from ornatus.models.design import DesignConcept, DesignRequest, GarmentSpecification, GarmentType

USER_ID = "user-1"


def make_request(request_id: str, **overrides) -> DesignRequest:
    defaults = dict(
        id=request_id,
        user_id=USER_ID,
        natural_language_request="I want a relaxed cream linen shirt for a summer dinner.",
    )
    defaults.update(overrides)
    return DesignRequest(**defaults)


def make_concept(concept_id: str, design_request_id: str, **overrides) -> DesignConcept:
    defaults = dict(
        id=concept_id,
        design_request_id=design_request_id,
        user_id=USER_ID,
        title="Relaxed Cream Linen Shirt",
        description="A relaxed cream linen shirt, suited for a summer dinner.",
        garment_specification=GarmentSpecification(
            garment_type=GarmentType.SHIRT, fit="relaxed", colors=["cream"], material="linen"
        ),
        rationale="Matches the request for a relaxed summer shirt.",
    )
    defaults.update(overrides)
    return DesignConcept(**defaults)


def test_design_request_add_and_get_round_trips(design_request_repository):
    request = make_request("design-1", occasion="summer dinner", desired_impression="relaxed")

    design_request_repository.add(request)
    fetched = design_request_repository.get("design-1")

    assert fetched is not None
    assert fetched.natural_language_request == request.natural_language_request
    assert fetched.occasion == "summer dinner"
    assert fetched.desired_impression == "relaxed"


def test_design_request_get_missing_returns_none(design_request_repository):
    assert design_request_repository.get("does-not-exist") is None


def test_design_request_list_for_user_scopes_by_user(design_request_repository):
    design_request_repository.add(make_request("design-1"))
    design_request_repository.add(make_request("design-2", user_id="user-2"))

    assert [r.id for r in design_request_repository.list_for_user(USER_ID)] == ["design-1"]


def test_design_concept_add_and_get_round_trips_specification(
    design_request_repository, design_concept_repository
):
    design_request_repository.add(make_request("design-1"))
    concept = make_concept("concept-1", "design-1")

    design_concept_repository.add(concept)
    fetched = design_concept_repository.get("concept-1")

    assert fetched is not None
    assert fetched.design_request_id == "design-1"
    assert fetched.garment_specification.garment_type == GarmentType.SHIRT
    assert fetched.garment_specification.material == "linen"
    assert fetched.garment_specification.colors == ["cream"]


def test_design_concept_get_missing_returns_none(design_concept_repository):
    assert design_concept_repository.get("does-not-exist") is None


def test_design_concept_list_for_request_relates_to_request(
    design_request_repository, design_concept_repository
):
    design_request_repository.add(make_request("design-1"))
    design_request_repository.add(make_request("design-2"))
    design_concept_repository.add(make_concept("concept-1", "design-1"))
    design_concept_repository.add(make_concept("concept-2", "design-2"))

    concepts_for_1 = design_concept_repository.list_for_request("design-1")

    assert [c.id for c in concepts_for_1] == ["concept-1"]


def test_design_concept_list_for_user_scopes_by_user(design_request_repository, design_concept_repository):
    design_request_repository.add(make_request("design-1"))
    design_concept_repository.add(make_concept("concept-1", "design-1"))
    design_concept_repository.add(make_concept("concept-2", "design-1", user_id="user-2"))

    assert [c.id for c in design_concept_repository.list_for_user(USER_ID)] == ["concept-1"]


def test_design_concept_get_latest_for_user_returns_most_recent(
    design_request_repository, design_concept_repository
):
    design_request_repository.add(make_request("design-1"))
    design_concept_repository.add(make_concept("concept-1", "design-1"))
    latest = make_concept("concept-2", "design-1")
    design_concept_repository.add(latest)

    assert design_concept_repository.get_latest_for_user(USER_ID).id == latest.id
