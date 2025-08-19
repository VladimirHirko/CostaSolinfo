import React from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import "../styles/breadcrumbs.css";

/** items: [{ to?: string, label: string }] */
export default function Breadcrumbs({ items = [] }) {
  const last = items.length - 1;
  return (
    <nav className="breadcrumbs" aria-label="Breadcrumb">
      <ol>
        {items.map((it, i) => (
          <li key={i} className={i === last ? "current" : ""}>
            {it.to && i !== last ? <Link to={it.to}>{it.label}</Link> : <span>{it.label}</span>}
          </li>
        ))}
      </ol>
    </nav>
  );
}
