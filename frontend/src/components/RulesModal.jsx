import React, { useEffect } from "react";
import DOMPurify from "dompurify";

export default function RulesModal({ open, onClose, html, title, okLabel = "OK" }) {
  useEffect(() => {
    if (!open) return;
    const onEsc = (e) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onEsc);
    return () => document.removeEventListener("keydown", onEsc);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label={title} onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{title}</h3>
          <button className="modal-close" onClick={onClose} aria-label="Close">×</button>
        </div>
        <div
          className="modal-body"
          dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(html, {
            ALLOWED_TAGS: ["div","h1","h2","h3","h4","p","ul","ol","li","strong","em","a","br","span","img"],
            ALLOWED_ATTR: ["href","target","rel","class","src","alt","title"]

          })}}
        />
        <div className="modal-footer">
          <button className="btn-primary" onClick={onClose}>{okLabel}</button>
        </div>
      </div>
    </div>
  );
}
