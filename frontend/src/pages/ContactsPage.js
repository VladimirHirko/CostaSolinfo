// frontend/src/pages/ContactsPage.js
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import '../styles/main.css';
import '../styles/contacts.css';
import { normalizeText } from '../helpers/normalizeText';

function ContactsPage() {
  const { t, i18n } = useTranslation();

  const [form, setForm] = useState({ name: '', email: '', question: '' });
  const [status, setStatus] = useState(null);        // 'success' | 'error' | null
  const [submitting, setSubmitting] = useState(false);

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const hasLettersOrNumbers = (s) => Array.from(s).some((ch) => /\p{Letter}|\p{Number}/u.test(ch));

  const onSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return;

    setStatus(null);
    setSubmitting(true);

    const payload = {
      name: normalizeText(form.name),
      email: normalizeText(form.email),
      language: i18n.language,
      question: normalizeText(form.question),   // 👈 единственное текстовое поле
      source: 'contacts',
      category: 'other',
    };

    // Клиентская проверка — чтобы не слать пустоту/невидимые символы
    if (!hasLettersOrNumbers(payload.question)) {
      setStatus('error');
      setSubmitting(false);
      return;
    }

    try {
      const res = await fetch('http://127.0.0.1:8000/api/contact-questions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept-Language': i18n.language,
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data?.message || 'send failed');

      // успех — чистим только сообщение, имя/почту можно оставить
      setStatus('success');
      setForm((prev) => ({ ...prev, question: '' }));
    } catch (err) {
      console.error('[Contacts] send error:', err);
      setStatus('error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <PageBanner page="contacts" />

      <div className="page-container">
        <p className="welcome-text text-center" style={{ textAlign: 'center', fontSize: '1.3em'}}>
          {t('contacts_intro')}
        </p>

        {/* Кликовые карточки */}
        <div className="contacts-grid contacts-grid-compact">
          <a className="contact-card link-card" href="mailto:CostaSolinfo.Malaga@gmail.com">
            <div className="cc-header">
              <span className="cc-icon" aria-hidden>
                <svg viewBox="0 0 24 24">
                  <path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Zm0 4-8 5L4 8"
                        fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              <h3 className="cc-title">{t('contacts_email')}</h3>
            </div>
          </a>

          <a className="contact-card link-card" href="https://wa.me/34660535089" target="_blank" rel="noreferrer">
            <div className="cc-header">
              <span className="cc-icon" aria-hidden>
                <svg viewBox="0 0 24 24">
                  <path d="M20 11.5A8.5 8.5 0 1 1 6.9 19L4 20l1-2.9A8.5 8.5 0 0 1 20 11.5Z"
                        fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              <h3 className="cc-title">WhatsApp</h3>
            </div>
          </a>

          <a className="contact-card link-card" href="https://t.me/your_channel_or_username" target="_blank" rel="noreferrer">
            <div className="cc-header">
              <span className="cc-icon" aria-hidden>
                <svg viewBox="0 0 24 24">
                  <path d="M21 3 8.5 12.5M21 3l-7 18-2.5-8.5L3 10l18-7Z"
                        fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              <h3 className="cc-title">{t('contacts_telegram')}</h3>
            </div>
          </a>
        </div>

        {/* Форма */}
        <div className="contact-form">
          <h3>{t('contacts_form_title')}</h3>

          <form onSubmit={onSubmit} className="contact-form-grid" noValidate>
            <div className="form-field">
              <label htmlFor="cf-name">{t('contacts_form_name')}</label>
              <input
                id="cf-name"
                type="text"
                name="name"
                value={form.name}
                onChange={onChange}
                className="transfer-input"
                autoComplete="name"
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="cf-email">{t('contacts_form_email')}</label>
              <input
                id="cf-email"
                type="email"
                name="email"
                value={form.email}
                onChange={onChange}
                className="transfer-input"
                autoComplete="email"
                required
              />
            </div>

            <div className="form-field form-field--full">
              <label htmlFor="cf-message">{t('contacts_form_message')}</label>
              <textarea
                id="cf-message"
                name="question"           // 👈 важно: одно имя на всех языках
                value={form.question}
                onChange={onChange}
                rows="5"
                className="transfer-input"
                required
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="transfer-button" disabled={submitting}>
                {submitting ? (t('loading') || 'Sending...') : (t('contacts_form_send') || 'Send')}
              </button>
            </div>
          </form>

          {status === 'success' && (
            <div className="success-message-box" style={{ marginTop: 12 }}>
              {t('contacts_form_success')}
            </div>
          )}
          {status === 'error' && (
            <div className="transfer-warning-box" style={{ marginTop: 12 }}>
              {t('contacts_form_error')}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default ContactsPage;
