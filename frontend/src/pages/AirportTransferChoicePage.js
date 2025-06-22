import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import '../styles/main.css'; // убедись, что подключены глобальные стили

function AirportTransferChoicePage() {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleChoice = (type) => {
    if (type === 'group') navigate('/airport-transfer/group');
    else if (type === 'private') navigate('/airport-transfer/private');
  };

  return (
    <div className="page-container">
      <PageBanner page="airport_transfer" />
      <h2 style={{ textAlign: 'center' }}>{t('transfer_to_airport')}</h2>
      <div className="transfer-buttons">
        <button onClick={() => handleChoice('group')} className="transfer-button">
          {t('group_transfer')}
        </button>
        <button onClick={() => handleChoice('private')} className="transfer-button">
          {t('private_transfer')}
        </button>
      </div>
    </div>
  );
}

export default AirportTransferChoicePage;
