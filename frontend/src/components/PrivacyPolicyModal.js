import React, { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import '../styles/PrivacyPolicyModal.css';

const FOCUSABLE_SELECTORS =
  'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])';

const PrivacyPolicyModal = ({ isOpen, onClose }) => {
  const { t, i18n } = useTranslation();
  const [policyText, setPolicyText] = useState('');
  const [loading, setLoading] = useState(true);

  const modalRef = useRef(null);               // контейнер модалки (для фокуса/ловушки)
  const previouslyFocusedRef = useRef(null);   // куда вернуть фокус после закрытия

  // Загрузка политики (с отменой на unmount/переключении языка)
  useEffect(() => {
    if (!isOpen) return;

    const controller = new AbortController();
    const fetchPolicy = async () => {
      try {
        setLoading(true);
        const res = await fetch(`/api/privacy-policy/?lang=${i18n.language}`, {
          headers: { 'Cache-Control': 'no-cache' },
          signal: controller.signal,
        });
        if (!res.ok || res.status === 204) throw new Error('Empty response');
        const data = await res.json();
        setPolicyText(data.content || t('policy_not_found'));
      } catch (err) {
        if (err.name !== 'AbortError') setPolicyText(t('error_loading_policy'));
      } finally {
        setLoading(false);
      }
    };

    fetchPolicy();
    return () => controller.abort();
  }, [isOpen, i18n.language, t]);

  // Блокировка скролла body + возврат фокуса после закрытия
  useEffect(() => {
    if (!isOpen) return;
    previouslyFocusedRef.current = document.activeElement;
    const { style } = document.body;
    const prevOverflow = style.overflow;
    style.overflow = 'hidden';

    return () => {
      style.overflow = prevOverflow;
      // Вернём фокус туда, где он был
      previouslyFocusedRef.current && previouslyFocusedRef.current.focus?.();
    };
  }, [isOpen]);

  // Фокус-ловушка + Escape
  useEffect(() => {
    if (!isOpen || !modalRef.current) return;

    const container = modalRef.current;
    const focusables = container.querySelectorAll(FOCUSABLE_SELECTORS);

    // Сфокусируем первый элемент внутри модалки (или сам контейнер)
    (focusables[0] || container).focus();

    const onKeyDown = (e) => {
      if (e.key === 'Escape') {
        e.stopPropagation();
        onClose?.();
        return;
      }
      if (e.key !== 'Tab') return;

      const list = container.querySelectorAll(FOCUSABLE_SELECTORS);
      if (!list.length) return;

      const first = list[0];
      const last = list[list.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    container.addEventListener('keydown', onKeyDown);
    return () => container.removeEventListener('keydown', onKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // Закрытие по клику на затемнение
  const onOverlayClick = (e) => {
    if (e.target === e.currentTarget) onClose?.();
  };

  return (
    <div className="modal-overlay" onClick={onOverlayClick}>
      <div
        className="modal-content"
        role="dialog"
        aria-modal="true"
        aria-labelledby="policy-title"
        aria-describedby="policy-text"
        ref={modalRef}
        tabIndex={-1}
      >
        <h2 id="policy-title">{t('privacy_policy')}</h2>

        {loading ? (
          <p aria-busy="true">{t('loading')}...</p>
        ) : (
          <div
            id="policy-text"
            className="policy-text"
            // HTML берётся из админки (CKEditor); отрисовываем, как задумано
            dangerouslySetInnerHTML={{ __html: policyText }}
          />
        )}

        <button className="transfer-button" onClick={onClose}>
          {t('close')}
        </button>
      </div>
    </div>
  );
};

export default PrivacyPolicyModal;
