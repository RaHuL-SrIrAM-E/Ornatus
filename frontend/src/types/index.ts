// Mirrors the FastAPI response shapes in ornatus/api/app.py exactly —
// keep these in sync with that module rather than inventing UI-only shapes.

export interface WardrobeItem {
  id: string;
  name: string;
  category: string;
  subcategory: string | null;
  colors: string[];
  material: string | null;
  pattern: string | null;
  formality: string;
  style_tags: string[];
}

export interface Recommendation {
  id: string;
  item_ids: string[];
  excluded_item_ids: string[];
  items: WardrobeItem[];
  excluded_items: WardrobeItem[];
  reasoning: string;
  confidence: number | null;
  event_reference: string | null;
  weather_summary: string | null;
}

export interface GarmentSpecification {
  garment_type: string;
  fit: string | null;
  silhouette: string | null;
  colors: string[];
  material: string | null;
  pattern: string | null;
  collar: string | null;
  sleeve: string | null;
  length: string | null;
  formality: string | null;
  season: string[];
  style_tags: string[];
  occasion: string | null;
  custom_details: Record<string, string>;
}

export interface DesignConcept {
  id: string;
  design_request_id: string;
  title: string;
  description: string;
  garment_specification: GarmentSpecification;
  rationale: string;
}

export type DecisionType = "outfit_recommendation" | "feedback" | "design_concept" | "other";

export interface ChatResponse {
  response: string;
  decision_id: string;
  decision_type: DecisionType;
  recommendation: Recommendation | null;
  design_concept: DesignConcept | null;
}

export interface HealthResponse {
  status: string;
  model_provider: string;
}
