// frontend/src/components/ExcursionLongDetailModal.jsx
import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { fetchExcursionLongDetail } from '../api/excursions';
import { useTranslation } from 'react-i18next';
// Для HTML всегда лучше DOMPurify:
const sanitize = (html) => html ?? "";

const modalRoot = document.getElementById('modal-root') || document.body;

export default function ExcursionLongDetailModal({ excursionId, isOpen, onClose }) {
  const { i18n, t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [payload, setPayload] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isOpen || !excursionId) return;
    let cancelled = false;

    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchExcursionLongDetail(excursionId, i18n.language || 'en');
        if (!cancelled) setPayload(data);
      } catch (e) {
        if (!cancelled) setError(e.message || 'Error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => { cancelled = true; };
  }, [isOpen, excursionId, i18n.language]);

  if (!isOpen) return null;

  return createPortal(
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{t('excursion.moreDetails', 'Подробное описание')}</h3>
          <button className="modal-close" onClick={onClose} aria-label="Close">×</button>
        </div>

        <div className="modal-body">
          {loading && <p>{t('common.loading', 'Загрузка…')}</p>}
          {error && <p className="error">{t('common.error', 'Ошибка')}: {error}</p>}

          {!loading && !error && (
            <>
              {(!payload || !payload.text?.trim()) ? (
                <p>{t('excursion.detailsComingSoon', 'Скоро добавим подробное описание для этой экскурсии.')}</p>
              ) : (
                <div className="prose" dangerouslySetInnerHTML={{ __html: sanitize(payload.text) }} />
              )}
              
            </>
          )}
        </div>
      </div>

      <style>{`
        .modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.45);
          display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 16px;}
        .modal-panel { background: #fff; max-width: 900px; width: 100%; border-radius: 16px;
          overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,.2); max-height: 85vh; display: flex; flex-direction: column;}
        .modal-header { display: flex; align-items: center; justify-content: space-between;
          padding: 16px 20px; border-bottom: 1px solid #eee;}
        .modal-body { padding: 16px 20px; overflow: auto; }
        .modal-close { font-size: 24px; line-height: 1; background: transparent; border: 0; cursor: pointer; }
        .prose p { margin: 0 0 0.75rem 0; }
        .prose ul { padding-left: 1.2rem; }
        .mt-4 { margin-top: 1rem; }
        .error { color: #b00020; }
      `}</style>
    </div>,
    modalRoot
  );
}
