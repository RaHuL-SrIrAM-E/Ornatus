import { useState } from "react";
import { chat, ApiError } from "../api/client";
import { ChatInput } from "../components/ChatInput";
import { Message } from "../components/Message";
import { DesignConceptCard } from "../components/DesignConceptCard";
import type { DesignConcept } from "../types";
import "./Create.css";

export function Create() {
  const [loading, setLoading] = useState(false);
  const [concept, setConcept] = useState<DesignConcept | null>(null);
  const [response, setResponse] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(message: string) {
    setLoading(true);
    setError(null);

    try {
      const result = await chat(message);
      setResponse(result.response);
      setConcept(result.design_concept);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="create">
      <section className="create__hero">
        <h1>Create something.</h1>
        <p className="create__subtitle">Tell me what you&rsquo;re imagining.</p>
      </section>

      <ChatInput
        placeholder="I want something elegant but effortless, not corporate, for a summer dinner."
        buttonLabel="Design it"
        loading={loading}
        onSubmit={handleSubmit}
      />

      {loading && <p className="create__thinking">Sketching a design…</p>}
      {error && <Message role="error" text={error} />}
      {!loading && response && !concept && <Message role="assistant" text={response} />}
      {concept && (
        <div className="create__result">
          <DesignConceptCard concept={concept} />
        </div>
      )}
    </div>
  );
}
