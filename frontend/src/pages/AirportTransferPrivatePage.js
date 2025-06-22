import React from 'react';
import { useTranslation } from 'react-i18next';

const AirportTransferPrivatePage = () => {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('private_transfer')}</h1>
      <p>{t('enter_hotel_and_date')}</p>
      {/* Здесь будет форма для индивидуального трансфера */}
    </div>
  );
};

export default AirportTransferPrivatePage;
