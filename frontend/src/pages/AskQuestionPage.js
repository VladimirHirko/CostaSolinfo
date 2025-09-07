// frontend/src/pages/AskQuestionPage.js
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import '../styles/main.css';
import { normalizeText } from '../helpers/normalizeText';

function AskQuestionPage() {
  const { t, i18n } = useTranslation();

  // 🔹 контент из админки (title + content)
  const [page, setPage] = useState({ title: '', content: '' });

  const [form, setForm] = useState({
    name: '',
    email: '',
    category: '',
    question: '',
  });
  const [status, setStatus] = useState(null);       // 'success' | 'error' | null
  const [submitting, setSubmitting] = useState(false);

  // 🔹 тянем контент страницы из API (фолбэк на i18n)
  useEffect(() => {
    fetch('/api/pages/ask/', { headers: { 'Accept-Language': i18n.language } })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((data) => setPage({
        title: data?.title || '',
        content: data?.content || '',
      }))
      .catch(() => setPage({ title: '', content: '' }));
  }, [i18n.language]);

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
      question: normalizeText(form.question),
      source: 'ask',
    };

    // не отправляем пустые/невидимые сообщения
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
      setForm((prev) => ({ ...prev, question: '' })); // чистим только поле вопроса
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
        <h2 className="ask-title">
          {page.title || t('ask_question')}
        </h2>

        {page.content ? (
          <div
            className="welcome-text"
            style={{ textAlign: 'left-aligned' }}
            // Контент из админки — доверенный HTML
            dangerouslySetInnerHTML={{ __html: page.content }}
          />
        ) : (
          <p className="ask-intro">
            {t('ask_intro')}
          </p>

        )}

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
            name="question"
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
