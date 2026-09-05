import { useEffect, useState } from "react";
import { getWardrobe, ApiError } from "../api/client";
import { WardrobeGrid } from "../components/WardrobeGrid";
import { Message } from "../components/Message";
import type { WardrobeItem } from "../types";
import "./Wardrobe.css";

export function Wardrobe() {
  const [items, setItems] = useState<WardrobeItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    getWardrobe()
      .then((result) => {
        if (!cancelled) setItems(result);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="wardrobe">
      <section className="wardrobe__hero">
        <h1>My wardrobe</h1>
      </section>

      {error && <Message role="error" text={error} />}

      {!error && items === null && <p className="wardrobe__loading">Loading your wardrobe…</p>}

      {!error && items !== null && (
        items.length === 0 ? (
          <p className="wardrobe__empty">Your wardrobe is empty for now.</p>
        ) : (
          <WardrobeGrid items={items} />
        )
      )}
    </div>
  );
}
