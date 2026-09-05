import type { ReactNode } from "react";
import { Navigation } from "./Navigation";
import "./Layout.css";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="layout">
      <Navigation />
      <main className="layout__content">{children}</main>
    </div>
  );
}
