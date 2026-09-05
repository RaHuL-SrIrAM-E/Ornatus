import "./Message.css";

interface MessageProps {
  role: "user" | "assistant" | "error";
  text: string;
}

export function Message({ role, text }: MessageProps) {
  return <p className={`message message--${role}`}>{text}</p>;
}
