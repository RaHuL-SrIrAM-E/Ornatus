import type { DesignConcept } from "../types";
import "./DesignConceptCard.css";

function titleCase(value: string): string {
  return value.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function DesignConceptCard({ concept }: { concept: DesignConcept }) {
  const spec = concept.garment_specification;

  const rawDetails: [string, string | null][] = [
    ["Garment", titleCase(spec.garment_type)],
    ["Fit", spec.fit],
    ["Silhouette", spec.silhouette],
    ["Material", spec.material],
    ["Color", spec.colors.length > 0 ? spec.colors.join(", ") : null],
    ["Pattern", spec.pattern],
    ["Occasion", spec.occasion],
    ["Formality", spec.formality],
  ];

  const details: [string, string][] = rawDetails
    .filter((entry): entry is [string, string] => Boolean(entry[1]))
    .map(([label, value]) => [label, titleCase(value)]);

  return (
    <div className="design-card">
      <div className="design-card__figure" aria-hidden="true">
        <span>Design preview coming soon</span>
      </div>

      <div className="design-card__content">
        <h2 className="design-card__title">{concept.title}</h2>
        <p className="design-card__description">{concept.description}</p>

        {details.length > 0 && (
          <dl className="design-card__details">
            {details.map(([label, value]) => (
              <div className="design-card__detail" key={label}>
                <dt>{label}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        )}

        {spec.style_tags.length > 0 && (
          <div className="design-card__tags">
            {spec.style_tags.map((tag) => (
              <span key={tag} className="design-card__tag">
                {tag}
              </span>
            ))}
          </div>
        )}

        <p className="design-card__rationale">{concept.rationale}</p>
      </div>
    </div>
  );
}
