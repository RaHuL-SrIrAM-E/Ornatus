"""Enums shared across domains (wardrobe items and the occasions they get
matched against) so they don't drift into two separate vocabularies.
"""

from enum import StrEnum


class Formality(StrEnum):
    CASUAL = "casual"
    SMART_CASUAL = "smart_casual"
    BUSINESS_CASUAL = "business_casual"
    FORMAL = "formal"


class Season(StrEnum):
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"
    ALL_SEASON = "all_season"
