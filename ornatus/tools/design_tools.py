"""Agent-facing tools over DesignService — clothing creation, distinct from
outfit recommendation (``ornatus.tools.outfit_tools``). Use these when the
user wants something they don't already own, not when composing from the
existing wardrobe. Thin wrappers, no reasoning here: the agent is expected
to have already turned the user's request into occasion/impression hints
and a structured garment specification before calling these.
"""

from strands import tool

from ornatus.services.design_service import DesignService, UnknownDesignRequestError


def make_design_tools(service: DesignService, user_id: str) -> list:
    @tool
    def create_design_request(
        natural_language_request: str,
        occasion: str | None = None,
        desired_impression: str | None = None,
        budget: float | None = None,
    ) -> dict:
        """Record that the user wants a new garment created, not one from
        their existing wardrobe. Call this first, before proposing a
        design, whenever the user describes clothing they want made rather
        than asking what to wear from what they own.

        Args:
            natural_language_request: The user's request, close to verbatim.
            occasion: The occasion this garment is for, if mentioned (e.g.
                "summer dinner").
            desired_impression: The look/feeling the user wants (e.g.
                "elegant but effortless, not corporate"), if they said so.
            budget: A budget, ONLY if the user explicitly gave one — never
                guess or estimate a price.

        Returns:
            The persisted design request as a structured dict, including
            its id — pass that id to save_design_concept next.
        """
        request = service.create_request(
            user_id,
            natural_language_request=natural_language_request,
            occasion=occasion,
            desired_impression=desired_impression,
            budget=budget,
        )
        return request.model_dump(mode="json")

    @tool
    def save_design_concept(
        design_request_id: str,
        title: str,
        description: str,
        rationale: str,
        garment_specification: dict,
    ) -> dict:
        """Persist a proposed garment design for a design request. Call
        this once you've worked out what the garment should be, after
        create_design_request.

        Args:
            design_request_id: The id returned by create_design_request.
            title: A short name for the design (e.g. "Relaxed Cream Linen
                Shirt").
            description: A human-readable description of the design, in
                plain language a person would actually say — this may be
                shown to the user directly.
            rationale: A brief explanation of why this design fits the
                user's request (occasion, desired impression, any
                constraints they gave).
            garment_specification: The structured design, as a dict with
                keys matching GarmentSpecification: garment_type (required
                — one of "shirt", "trousers", "dress", "jacket",
                "outerwear", "skirt", "sweater", "accessory", "other"),
                fit, silhouette, colors (list of strings), material,
                pattern, collar, sleeve, length, formality (one of
                "casual", "smart_casual", "business_casual", "formal"),
                season (list of "spring"/"summer"/"fall"/"winter"/
                "all_season"), style_tags (list of strings), occasion,
                custom_details (a dict of any other attribute names to
                values not covered above).

        Returns:
            The persisted design concept as a structured dict, including
            its id.

        Raises:
            ValueError: If design_request_id doesn't reference a real
                design request, or garment_specification doesn't conform
                to the expected shape.
        """
        try:
            concept = service.create_concept(
                user_id,
                design_request_id=design_request_id,
                title=title,
                description=description,
                garment_specification=garment_specification,
                rationale=rationale,
            )
        except UnknownDesignRequestError as exc:
            raise ValueError(str(exc)) from exc
        return concept.model_dump(mode="json")

    @tool
    def get_design_concept(concept_id: str) -> dict | None:
        """Retrieve a single previously saved design concept by id.

        Args:
            concept_id: The design concept's id.

        Returns:
            The concept as a structured dict, or null if no such concept
            exists.
        """
        concept = service.get_concept(concept_id)
        return concept.model_dump(mode="json") if concept else None

    @tool
    def list_design_concepts(design_request_id: str | None = None) -> list[dict]:
        """List previously saved design concepts for this user. Useful
        when the user refers back to a design they discussed earlier
        (e.g. "make that shirt in a different color").

        Args:
            design_request_id: Optional — scope to concepts for one
                specific design request. Omit to list every concept this
                user has.

        Returns:
            A list of design concepts as structured dicts.
        """
        if design_request_id is not None:
            concepts = service.list_concepts_for_request(design_request_id)
        else:
            concepts = service.list_concepts_for_user(user_id)
        return [c.model_dump(mode="json") for c in concepts]

    return [create_design_request, save_design_concept, get_design_concept, list_design_concepts]
