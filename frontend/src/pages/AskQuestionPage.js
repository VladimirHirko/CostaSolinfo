import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import '../styles/main.css';

function AskQuestionPage() {
  const { t, i18n } = useTranslation();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    category: '',
    question: '',
  });
  const [status, setStatus] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const data = { ...formData, language: i18n.language };

    fetch('http://localhost:8000/api/contact-questions/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept-Language': i18n.language,
      },
      body: JSON.stringify(data),
    })
      .then((res) => {
        if (res.ok) {
          setStatus('success');
          setFormData({ name: '', email: '', category: '', message: '' });
        } else {
          throw new Error('Ошибка отправки формы');
        }
      })
      .catch(() => setStatus('error'));
  };

  return (
    <div className="page-container">
      <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>
        {t('ask_question')}
      </h2>
      <p className="welcome-text" style={{ textAlign: 'center' }}>
        {t('ask_intro')}
      </p>

      <form className="transfer-form left-aligned" onSubmit={handleSubmit}>
        <label htmlFor="name">{t('your_name')}</label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className="transfer-input"
          required
        />

        <label htmlFor="email">{t('your_email')}</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          className="transfer-input"
          required
        />

        <label htmlFor="category">{t('question_category')}</label>
        <select
          id="category"
          name="category"
          value={formData.category}
          onChange={handleChange}
          className="transfer-input"
          required
        >
          <option value="">{t('select_category')}</option>
          <option value="transfer">{t('category_transfer')}</option>
          <option value="excursion">{t('category_excursion')}</option>
          <option value="organization">{t('category_organization')}</option>
          <option value="other">{t('category_other')}</option>
        </select>

        <label htmlFor="message">{t('your_question')}</label>
        <textarea
          id="question"
          name="question"
          rows="5"
          value={formData.message}
          onChange={handleChange}
          className="transfer-input"
          required
        ></textarea>

        <button type="submit" className="transfer-button" style={{ marginTop: '20px', alignSelf: "flex-start" }}>
          {t('send_question')}
        </button>
      </form>

      {status === 'success' && (
        <div className="success-message-box">
          {t('success_message')}
        </div>
      )}
      {status === 'error' && (
        <div className="transfer-warning-box">
          {t('error_message')}
        </div>
      )}
    </div>
  );
}

export default AskQuestionPage;
