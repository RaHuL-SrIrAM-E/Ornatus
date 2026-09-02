"""Agent-facing tool over PreferenceService."""

from strands import tool

from ornatus.services.preference_service import PreferenceService


def make_preference_tools(service: PreferenceService, user_id: str) -> list:
    @tool
    def get_user_preferences(context: str | None = None) -> list[dict]:
        """Look up what's already known about this user's likes/dislikes,
        learned from their past feedback. Useful before finalizing an
        outfit recommendation — especially when a wardrobe item was
        previously rejected, or a similar occasion has come up before.
        Not every request needs this: skip it when there's no plausible
        reason prior feedback would apply (e.g. a brand-new kind of
        request).

        Args:
            context: Optional occasion/context to scope results to (e.g.
                "client dinner"). When given, context-specific preferences
                that match it are included alongside item/category/general
                preferences, which always apply regardless of context.

        Returns:
            A list of learned preference signals as structured dicts: id,
            type (e.g. "item_dislike", "context_dislike"), value (what it's
            about — an item id, category, or descriptor), context, reason,
            confidence, created_at.
        """
        preferences = service.get_preferences(user_id, context=context)
        return [p.model_dump(mode="json") for p in preferences]

    return [get_user_preferences]
