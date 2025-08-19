import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { getConsent, setConsent } from '../utils/cookies';
import './CookieBanner.css';

export default function CookieBanner() {
  const { t, ready } = useTranslation();
  const [open, setOpen] = useState(false);
  const [state, setState] = useState({
    essential: true, analytics: false, marketing: false, preferences: false,
  });

  // Показать баннер, если согласия нет
  useEffect(() => {
    if (!getConsent()) setOpen(true);
  }, []);

  // Блокируем прокрутку страницы, когда модалка открыта
  useEffect(() => {
    if (!open) { document.body.style.overflow = ''; return; }
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = prev; };
  }, [open]);

  // Дадим способ открыть «Настройки cookies» из любого места (например, из футера)
  useEffect(() => {
    window.csiOpenCookieSettings = () => setOpen(true);
    return () => { delete window.csiOpenCookieSettings; };
  }, []);

  const close = () => setOpen(false);

  const acceptAll = () => {
    setConsent({ essential: true, analytics: true, marketing: true, preferences: true, ts: Date.now() });
    close();
  };
  const rejectAll = () => {
    setConsent({ essential: true, analytics: false, marketing: false, preferences: false, ts: Date.now() });
    close();
  };
  const saveSelection = () => {
    setConsent({ ...state, ts: Date.now() });
    close();
  };

  if (!open || !ready) return null;

  return (
    <div className="csi-cookie-overlay" role="dialog" aria-modal="true" aria-labelledby="cookies-title">
      <div className="csi-cookie-modal">
        <button className="csi-close" aria-label="Close" onClick={close}>×</button>

        <div className="csi-cookie-hero">
          <div className="csi-cookie-icon" aria-hidden>🍪</div>
          <div>
            <h4 id="cookies-title">{t('cookies.title')}</h4>
            <p className="csi-sub">{t('cookies.desc')}</p>
          </div>
        </div>

        <div className="csi-cookie-switches">
          <label className="csi-row">
            <input type="checkbox" checked readOnly />
            <span>{t('cookies.essential')}</span>
          </label>
          <label className="csi-row">
            <input type="checkbox" checked={state.analytics}
                   onChange={e=>setState(s=>({...s, analytics:e.target.checked}))}/>
            <span>{t('cookies.analytics')}</span>
          </label>
          <label className="csi-row">
            <input type="checkbox" checked={state.marketing}
                   onChange={e=>setState(s=>({...s, marketing:e.target.checked}))}/>
            <span>{t('cookies.marketing')}</span>
          </label>
          <label className="csi-row">
            <input type="checkbox" checked={state.preferences}
                   onChange={e=>setState(s=>({...s, preferences:e.target.checked}))}/>
            <span>{t('cookies.preferences')}</span>
          </label>
        </div>

        <div className="csi-cookie-actions">
          <button className="csi-btn primary" onClick={acceptAll}>{t('cookies.accept_all')}</button>
          <button className="csi-btn ghost" onClick={rejectAll}>{t('cookies.reject_all')}</button>
          <button className="csi-btn" onClick={saveSelection}>{t('cookies.save')}</button>
        </div>

        <p className="csi-note">
          <a
            href="#"
            className="csi-link"
            onClick={(e) => { e.preventDefault(); window.csiOpenPrivacy?.(); }}
          >
            {t('privacy_policy')}
          </a>
        </p>
      </div>
    </div>
  );
}
