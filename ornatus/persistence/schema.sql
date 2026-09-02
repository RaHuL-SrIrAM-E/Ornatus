-- Ornatus SQLite schema.
--
-- Complex/list fields (colors, style_tags, candidate_products, payload, ...)
-- are stored as JSON text. Each entity mirrors a model in ornatus.models.
-- wardrobe_items, outfit_recommendations, agent_decisions and feedback have
-- repository implementations (the first end-to-end agent workflow). The
-- remaining tables exist so the schema matches the full data model from day
-- one, without forcing unused repository code into the codebase yet.

CREATE TABLE IF NOT EXISTS user_profiles (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    locations TEXT NOT NULL DEFAULT '[]',
    sizing TEXT NOT NULL DEFAULT '{}',
    budget_monthly REAL,
    lifestyle_tags TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS preferences (
    user_id TEXT PRIMARY KEY,
    style_keywords TEXT NOT NULL DEFAULT '[]',
    preferred_colors TEXT NOT NULL DEFAULT '[]',
    avoided_colors TEXT NOT NULL DEFAULT '[]',
    avoided_materials TEXT NOT NULL DEFAULT '[]',
    preferred_brands TEXT NOT NULL DEFAULT '[]',
    avoided_brands TEXT NOT NULL DEFAULT '[]',
    fit_preferences TEXT NOT NULL DEFAULT '[]',
    price_sensitivity TEXT NOT NULL DEFAULT 'moderate',
    learned_weights TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS wardrobe_items (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT,
    colors TEXT NOT NULL DEFAULT '[]',
    pattern TEXT,
    material TEXT,
    brand TEXT,
    size TEXT,
    fit TEXT,
    formality TEXT NOT NULL DEFAULT 'casual',
    season TEXT NOT NULL DEFAULT '["all_season"]',
    suitable_occasions TEXT NOT NULL DEFAULT '[]',
    style_tags TEXT NOT NULL DEFAULT '[]',
    image_urls TEXT NOT NULL DEFAULT '[]',
    purchase_date TEXT,
    purchase_price REAL,
    source TEXT NOT NULL DEFAULT 'manual',
    status TEXT NOT NULL DEFAULT 'active',
    wear_count INTEGER NOT NULL DEFAULT 0,
    last_worn_date TEXT,
    condition TEXT,
    care_instructions TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_wardrobe_items_user ON wardrobe_items (user_id);

CREATE TABLE IF NOT EXISTS outfit_recommendations (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    request_text TEXT NOT NULL,
    event_reference TEXT,
    weather_summary TEXT,
    item_ids TEXT NOT NULL DEFAULT '[]',
    reasoning TEXT NOT NULL,
    confidence REAL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_outfit_recommendations_user ON outfit_recommendations (user_id);

CREATE TABLE IF NOT EXISTS agent_decisions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    user_request TEXT NOT NULL,
    decision_type TEXT NOT NULL,
    tools_used TEXT NOT NULL DEFAULT '[]',
    selected_item_ids TEXT NOT NULL DEFAULT '[]',
    reasoning_summary TEXT NOT NULL,
    outcome TEXT NOT NULL DEFAULT 'completed',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_agent_decisions_user ON agent_decisions (user_id);

CREATE TABLE IF NOT EXISTS feedback (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    recommendation_id TEXT,
    feedback_text TEXT NOT NULL,
    rejected_item_ids TEXT NOT NULL DEFAULT '[]',
    preference_signal TEXT NOT NULL DEFAULT 'neutral',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback (user_id);

CREATE TABLE IF NOT EXISTS outfit_history (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    outfit_date TEXT NOT NULL,
    item_ids TEXT NOT NULL DEFAULT '[]',
    occasion TEXT,
    weather_summary TEXT,
    calendar_event_ref TEXT,
    feedback TEXT NOT NULL DEFAULT 'pending',
    rating INTEGER,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_outfit_history_user ON outfit_history (user_id);

CREATE TABLE IF NOT EXISTS purchases (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    trigger TEXT NOT NULL,
    structured_requirement TEXT NOT NULL DEFAULT '{}',
    candidate_products TEXT NOT NULL DEFAULT '[]',
    selected_product TEXT,
    approval_status TEXT NOT NULL DEFAULT 'pending',
    approved_at TEXT,
    order_status TEXT NOT NULL DEFAULT 'not_ordered',
    order_id TEXT,
    cost REAL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_purchases_user ON purchases (user_id);

CREATE TABLE IF NOT EXISTS deliveries (
    id TEXT PRIMARY KEY,
    purchase_id TEXT NOT NULL,
    carrier TEXT,
    tracking_number TEXT,
    status TEXT NOT NULL DEFAULT 'in_transit',
    expected_date TEXT,
    actual_date TEXT,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_deliveries_purchase ON deliveries (purchase_id);

CREATE TABLE IF NOT EXISTS returns (
    id TEXT PRIMARY KEY,
    purchase_id TEXT NOT NULL,
    item_id TEXT,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'initiated',
    refund_amount REAL,
    initiated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_returns_purchase ON returns (purchase_id);

CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    type TEXT NOT NULL,
    payload TEXT NOT NULL DEFAULT '{}',
    occurred_at TEXT NOT NULL,
    processed INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_events_user ON events (user_id);

CREATE TABLE IF NOT EXISTS agent_memory (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    source_event_ref TEXT,
    confidence REAL NOT NULL DEFAULT 1.0,
    created_at TEXT NOT NULL,
    superseded_by TEXT
);
CREATE INDEX IF NOT EXISTS idx_agent_memory_user ON agent_memory (user_id);
