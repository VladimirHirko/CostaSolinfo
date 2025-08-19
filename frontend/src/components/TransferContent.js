// frontend/src/components/TransferContent.js
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

export default function TransferContent({ page }) {
  const { i18n } = useTranslation();
  const [blocks, setBlocks] = useState([]);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/transfer-content/${page}/?lang=${i18n.language}`)
      .then(r => r.json())
      .then(setBlocks)
      .catch(() => setBlocks([]));
  }, [page, i18n.language]);

  if (!blocks.length) return null;

  return (
    <div className="page-container" style={{ marginTop: 16 }}>
      {blocks.map(b => (
        <section key={b.id} style={{ marginBottom: 24 }}>
          {b.title && <h3 style={{ marginBottom: 8 }}>{b.title}</h3>}
          {/* контент из админки — HTML (CKEditor), рендерим осознанно */}
          <div dangerouslySetInnerHTML={{ __html: b.content }} />
        </section>
      ))}
    </div>
  );
}
