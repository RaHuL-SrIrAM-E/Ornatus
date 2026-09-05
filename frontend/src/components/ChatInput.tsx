import { useState } from "react";
import type { FormEvent } from "react";
import "./ChatInput.css";

interface ChatInputProps {
  placeholder: string;
  buttonLabel: string;
  loading: boolean;
  onSubmit: (message: string) => void;
}

export function ChatInput({ placeholder, buttonLabel, loading, onSubmit }: ChatInputProps) {
  const [value, setValue] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || loading) return;
    onSubmit(trimmed);
    setValue("");
  }

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <textarea
        className="chat-input__field"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder={placeholder}
        rows={2}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            handleSubmit(event);
          }
        }}
      />
      <button className="chat-input__submit" type="submit" disabled={loading || !value.trim()}>
        {loading ? "…" : buttonLabel}
      </button>
    </form>
  );
}
