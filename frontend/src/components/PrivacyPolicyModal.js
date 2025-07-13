import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import '../styles/PrivacyPolicyModal.css';

const PrivacyPolicyModal = ({ isOpen, onClose }) => {
  const { t, i18n } = useTranslation();
  const [policyText, setPolicyText] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      const fetchPolicy = async () => {
        try {
          setLoading(true);
          const res = await fetch(`/api/privacy-policy/?lang=${i18n.language}`, {
            headers: {
              'Cache-Control': 'no-cache',
            },
          });

          if (!res.ok || res.status === 204) {
            throw new Error('Empty response');
          }

          const data = await res.json();
          setPolicyText(data.content || t('policy_not_found'));
        } catch (error) {
          setPolicyText(t('error_loading_policy'));
        } finally {
          setLoading(false);
        }
      };


      fetchPolicy();
    }
  }, [isOpen, i18n.language, t]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>{t('privacy_policy')}</h2>
        {loading ? (
          <p>{t('loading')}...</p>
        ) : (
          <div className="policy-text" dangerouslySetInnerHTML={{ __html: policyText }} />
        )}
        <button className="transfer-button" onClick={onClose}>
          {t('close')}
        </button>
      </div>
    </div>
  );
};

export default PrivacyPolicyModal;
