import type { Recommendation } from "../types";
import "./OutfitCard.css";

export function OutfitCard({ recommendation }: { recommendation: Recommendation }) {
  const { items, excluded_items, reasoning, event_reference, weather_summary } = recommendation;

  return (
    <div className="outfit-card">
      {event_reference && <p className="outfit-card__eyebrow">{event_reference}</p>}

      <div className="outfit-card__pieces">
        {items.map((item, index) => (
          <div key={item.id} className="outfit-card__piece-wrap">
            <p className="outfit-card__piece">{item.name}</p>
            {index < items.length - 1 && <span className="outfit-card__divider">+</span>}
          </div>
        ))}
      </div>

      {reasoning && <p className="outfit-card__reasoning">&ldquo;{reasoning}&rdquo;</p>}

      {(weather_summary || excluded_items.length > 0) && (
        <div className="outfit-card__footnote">
          {weather_summary && <span>{weather_summary}</span>}
          {excluded_items.length > 0 && (
            <span>Left out: {excluded_items.map((item) => item.name).join(", ")}</span>
          )}
        </div>
      )}
    </div>
  );
}
