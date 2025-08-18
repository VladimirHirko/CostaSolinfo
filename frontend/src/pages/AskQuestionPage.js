// frontend/src/pages/AskQuestionPage.js
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import '../styles/main.css';
import { normalizeText } from '../helpers/normalizeText';

function AskQuestionPage() {
  const { t, i18n } = useTranslation();

  const [form, setForm] = useState({
    name: '',
    email: '',
    category: '',
    question: '',
  });
  const [status, setStatus] = useState(null);       // 'success' | 'error' | null
  const [submitting, setSubmitting] = useState(false);

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const hasLettersOrNumbers = (s) =>
    Array.from(s).some((ch) => /\p{Letter}|\p{Number}/u.test(ch));

  const onSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return;

    setStatus(null);
    setSubmitting(true);

    const payload = {
      name: normalizeText(form.name),
      email: normalizeText(form.email),
      category: form.category || 'other',
      language: i18n.language,
      question: normalizeText(form.question),   // 👈 единственное текстовое поле
      source: 'ask',
    };

    // клиентская проверка — не слать пустые/невидимые строки
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

      setStatus('success');
      // очищаем только сообщение, имя/почту/категорию можно оставить
      setForm((prev) => ({ ...prev, question: '' }));
    } catch (err) {
      console.error('[AskQuestion] send error:', err);
      setStatus('error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <PageBanner page="ask" />

      <div className="page-container">
        <h2 style={{ textAlign: 'center', marginBottom: 20 }}>
          {t('ask_question')}
        </h2>
        <p className="welcome-text" style={{ textAlign: 'center' }}>
          {t('ask_intro')}
        </p>

        <form className="transfer-form left-aligned" onSubmit={onSubmit} noValidate>
          <label htmlFor="aq-name">{t('your_name')}</label>
          <input
            id="aq-name"
            type="text"
            name="name"
            value={form.name}
            onChange={onChange}
            className="transfer-input"
            autoComplete="name"
            required
          />

          <label htmlFor="aq-email">{t('your_email')}</label>
          <input
            id="aq-email"
            type="email"
            name="email"
            value={form.email}
            onChange={onChange}
            className="transfer-input"
            autoComplete="email"
            required
          />

          <label htmlFor="aq-category">{t('question_category')}</label>
          <select
            id="aq-category"
            name="category"
            value={form.category}
            onChange={onChange}
            className="transfer-input"
            required
          >
            <option value="">{t('select_category')}</option>
            <option value="transfer">{t('category_transfer')}</option>
            <option value="excursion">{t('category_excursion')}</option>
            <option value="organization">{t('category_organization')}</option>
            <option value="other">{t('category_other')}</option>
          </select>

          <label htmlFor="aq-question">{t('your_question')}</label>
          <textarea
            id="aq-question"
            name="question"             // 👈 важно: одно имя на всех языках
            rows="5"
            value={form.question}
            onChange={onChange}
            className="transfer-input"
            required
          />

          <button
            type="submit"
            className="transfer-button"
            style={{ marginTop: 20, alignSelf: 'flex-start' }}
            disabled={submitting}
          >
            {submitting ? (t('loading') || 'Sending...') : (t('send_question') || 'Send')}
          </button>
        </form>

        {status === 'success' && (
          <div className="success-message-box" style={{ marginTop: 12 }}>
            {t('success_message')}
          </div>
        )}
        {status === 'error' && (
          <div className="transfer-warning-box" style={{ marginTop: 12 }}>
            {t('error_message')}
          </div>
        )}
      </div>
    </>
  );
}

export default AskQuestionPage;
