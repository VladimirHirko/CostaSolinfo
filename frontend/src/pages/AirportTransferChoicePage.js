import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import '../styles/main.css'; // убедись, что подключены глобальные стили
import TransferContent from '../components/TransferContent';
import Breadcrumbs from "../components/Breadcrumbs";


function AirportTransferChoicePage() {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleChoice = (type) => {
    if (type === 'group') navigate('/airport-transfer/group');
    else if (type === 'private') navigate('/airport-transfer/private');
  };

  return (
    <>
      <PageBanner page="airport_transfer" />            

      <div className="page-container">
        <Breadcrumbs items={[
          { to: "/", label: t("home") },
          { label: t("airport_transfer") }
        ]}/>

      <TransferContent page="transfer_home" />

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
    </>
  );
}

export default AirportTransferChoicePage;
