from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    user_id: str
    name: str
    locations: list[str] = Field(default_factory=list)
    sizing: dict[str, str] = Field(default_factory=dict)  # brand -> size
    budget_monthly: float | None = None
    lifestyle_tags: list[str] = Field(default_factory=list)
