import type { WardrobeItem } from "../types";
import "./ClothingItemCard.css";

export function ClothingItemCard({ item }: { item: WardrobeItem }) {
  const metaLine = [item.material, item.colors[0]].filter(Boolean).join(" · ");

  return (
    <div className="item-card">
      <div className="item-card__swatch" aria-hidden="true">
        <span>{item.category.slice(0, 1).toUpperCase()}</span>
      </div>
      <div className="item-card__body">
        <p className="item-card__name">{item.name}</p>
        <p className="item-card__category">{item.subcategory ?? item.category}</p>
        {metaLine && <p className="item-card__meta">{metaLine}</p>}
      </div>
    </div>
  );
}
