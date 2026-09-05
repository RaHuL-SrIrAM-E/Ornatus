import { useState } from "react";
import { chat, ApiError } from "../api/client";
import { ChatInput } from "../components/ChatInput";
import { Message } from "../components/Message";
import { OutfitCard } from "../components/OutfitCard";
import type { Recommendation } from "../types";
import "./Home.css";

interface Turn {
  id: string;
  request: string;
  response?: string;
  recommendation?: Recommendation | null;
  error?: string;
}

function greeting(): string {
  const hour = new Date().getHours();
  if (hour < 5) return "Good evening.";
  if (hour < 12) return "Good morning.";
  if (hour < 18) return "Good afternoon.";
  return "Good evening.";
}

export function Home() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(message: string) {
    const id = crypto.randomUUID();
    setTurns((prev) => [...prev, { id, request: message }]);
    setLoading(true);

    try {
      const result = await chat(message);
      setTurns((prev) =>
        prev.map((turn) =>
          turn.id === id ? { ...turn, response: result.response, recommendation: result.recommendation } : turn,
        ),
      );
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : "Something went wrong. Please try again.";
      setTurns((prev) => prev.map((turn) => (turn.id === id ? { ...turn, error: errorMessage } : turn)));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="home">
      <section className="home__hero">
        <h1 className="home__greeting">{greeting()}</h1>
        <p className="home__prompt">What can I take care of?</p>
      </section>

      <ChatInput
        placeholder="What should I wear...?"
        buttonLabel="Ask"
        loading={loading}
        onSubmit={handleSubmit}
      />

      {turns.length === 0 ? (
        <p className="home__hint">
          Try: &ldquo;What should I wear to my client dinner Friday?&rdquo;
        </p>
      ) : (
        <div className="home__conversation">
          {turns.map((turn) => (
            <div key={turn.id} className="home__turn">
              <Message role="user" text={turn.request} />
              {turn.error && <Message role="error" text={turn.error} />}
              {turn.response && <Message role="assistant" text={turn.response} />}
              {turn.recommendation && <OutfitCard recommendation={turn.recommendation} />}
            </div>
          ))}
          {loading && <p className="home__thinking">Thinking…</p>}
        </div>
      )}
    </div>
  );
}
