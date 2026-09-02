from pydantic import BaseModel, Field


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
