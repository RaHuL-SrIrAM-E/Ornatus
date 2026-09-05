import { useMemo, useState } from "react";
import type { WardrobeItem } from "../types";
import { ClothingItemCard } from "./ClothingItemCard";
import "./WardrobeGrid.css";

const FILTERS: { label: string; category: string | null }[] = [
  { label: "All", category: null },
  { label: "Shirts", category: "top" },
  { label: "Trousers", category: "bottom" },
  { label: "Outerwear", category: "outerwear" },
  { label: "Shoes", category: "shoes" },
];

export function WardrobeGrid({ items }: { items: WardrobeItem[] }) {
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  const visibleItems = useMemo(
    () => (activeCategory ? items.filter((item) => item.category === activeCategory) : items),
    [items, activeCategory],
  );

  return (
    <div className="wardrobe-grid">
      <div className="wardrobe-grid__filters">
        {FILTERS.map((filter) => (
          <button
            key={filter.label}
            className={
              "wardrobe-grid__filter" + (activeCategory === filter.category ? " wardrobe-grid__filter--active" : "")
            }
            onClick={() => setActiveCategory(filter.category)}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {visibleItems.length === 0 ? (
        <p className="wardrobe-grid__empty">Nothing here yet.</p>
      ) : (
        <div className="wardrobe-grid__items">
          {visibleItems.map((item) => (
            <ClothingItemCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}
