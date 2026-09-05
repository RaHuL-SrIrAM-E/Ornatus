import { NavLink } from "react-router-dom";
import "./Navigation.css";

const LINKS = [
  { to: "/", label: "Home" },
  { to: "/wardrobe", label: "Wardrobe" },
  { to: "/create", label: "Create" },
];

export function Navigation() {
  return (
    <header className="nav">
      <div className="nav__inner">
        <span className="nav__brand">Ornatus</span>
        <nav className="nav__links">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              className={({ isActive }) => "nav__link" + (isActive ? " nav__link--active" : "")}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}
