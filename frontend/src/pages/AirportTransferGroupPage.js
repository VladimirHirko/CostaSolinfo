// frontend/src/pages/AirportTransferGroupPage.js
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import DatePicker from 'react-datepicker';
import TransferMap from '../components/TransferMap';
import 'react-datepicker/dist/react-datepicker.css';

const AirportTransferGroupPage = () => {
  const { t } = useTranslation();
  const [hotel, setHotel] = useState('');
  const [hotelId, setHotelId] = useState(null);
  const [hotelSuggestions, setHotelSuggestions] = useState([]);
  const [suggestionsVisible, setSuggestionsVisible] = useState(false);
  const [date, setDate] = useState(null);
  const [pickupTime, setPickupTime] = useState('');
  const [pickupPoint, setPickupPoint] = useState('');
  const [pickupCoords, setPickupCoords] = useState(null);
  const [email, setEmail] = useState('');
  const [checkboxAccepted, setCheckboxAccepted] = useState(false);
  const [emailSentMessage, setEmailSentMessage] = useState('');

  const [error, setError] = useState('');

  // 🔹 Загрузка отелей при вводе
  useEffect(() => {
    if (hotel.length >= 2) {
      fetch(`http://localhost:8000/api/hotels/?search=${hotel}`)
        .then((res) => res.json())
        .then((data) => {
          setHotelSuggestions(data);
          setSuggestionsVisible(true);
        })
        .catch((err) => console.error('Ошибка загрузки отелей:', err));
    } else {
      setHotelSuggestions([]);
      setSuggestionsVisible(false);
    }
  }, [hotel]);

  // 🔹 Выбор отеля из подсказки
  const handleSelectHotel = (name, id) => {
    setHotel(name);
    setHotelId(id);
    setHotelSuggestions([]);
    setSuggestionsVisible(false);
    setTimeout(() => {
      document.activeElement.blur();
    }, 0);
  };


  // 🔹 Отправка формы
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!hotelId || !date) {
      setError(t('please_fill_all_fields'));
      return;
    }

    try {
      const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
      const dateStr = localDate.toISOString().split('T')[0];

      const url = `http://localhost:8000/api/transfer-schedule/?hotel_id=${hotelId}&date=${dateStr}&type=group`;

      const response = await fetch(url);
      const data = await response.json();

      if (response.ok) {
        setPickupTime(data.pickup_time || '');
        setPickupPoint(data.pickup_point || '');
        setPickupCoords({ lat: data.pickup_lat, lng: data.pickup_lng });
        setError('');
      } else {
        setPickupTime('');
        setPickupPoint('');
        setPickupCoords(null);
        setError(data.error || t('something_went_wrong'));
      }
    } catch (err) {
      console.error(err);
      setError(t('something_went_wrong'));
    }
  };

  // Отправка писем об изменении трансфера и их подписки
  const handleEmailSubmit = async () => {
    if (!email || !checkboxAccepted || !hotelId || !date) return;

    try {
      const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
      const dateStr = localDate.toISOString().split('T')[0];

      const response = await fetch('http://localhost:8000/api/transfer-notifications/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email,
          hotel: hotelId,  // ✅ Важно: заменили hotel_id на hotel
          transfer_type: 'group',
          departure_date: dateStr,
          language: 'ru'  // позже сделаем автоопределение
        })
      });

      if (response.ok) {
        setEmailSentMessage(t('email_sent_success'));
        setEmail('');
        setCheckboxAccepted(false);
      } else {
        const data = await response.json();
        console.error('Ошибка отправки:', data);
        setEmailSentMessage(t('email_send_error'));
      }
    } catch (err) {
      console.error(err);
      setEmailSentMessage(t('email_send_error'));
    }
  };




  return (
    <div className="page-container">
      <PageBanner page="group_transfer" />
      <h1>{t('group_transfer')}</h1>
      <p>{t('enter_hotel_and_date')}</p>

      <form onSubmit={handleSubmit} className="transfer-form left-aligned">
        {/* 🔹 Отель */}
        <label>{t('enter_hotel')}</label>
        <div className="autocomplete-wrapper">
          <input
            type="text"
            value={hotel}
            onChange={(e) => setHotel(e.target.value)}
            placeholder={t('enter_hotel')}
            className="transfer-input"
          />
          {hotelSuggestions.length > 0 && !hotelSuggestions.some(h => h.name === hotel) && (
            <ul className="autocomplete-list">
              {hotelSuggestions.map((item) => (
                <li key={item.id} onMouseDown={() => handleSelectHotel(item.name, item.id)}>
                  {item.name}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* 🔹 Дата */}
        <label>{t('select_date')}</label>
        <DatePicker
          selected={date}
          onChange={(date) => setDate(date)}
          placeholderText={t('select_date')}
          className="transfer-input"
          dateFormat="yyyy-MM-dd"
        />

        {/* 🔹 Кнопка */}
        <button type="submit" className="transfer-button">
          {t('show_transfer_time')}
        </button>
      </form>

      {/* 🔹 Ошибка */}
      {error && <p className="error-message">{error}</p>}

      {/* 🔹 Результат */}
      {pickupTime && (
        <div className="transfer-result">
          <h3>{t('pickup_time')}:</h3>
          <p>{pickupTime}</p>
          {pickupPoint && <p>{t('pickup_point')}: {pickupPoint}</p>}

          {/* 🔹 Вставляем карту только если есть координаты */}
          {pickupCoords && (
            <div style={{ height: '400px', marginTop: '20px' }}>
              <TransferMap
                lat={pickupCoords.lat}
                lng={pickupCoords.lng}
                pickupName={pickupPoint}
              />
            </div>
          )}
          {/* 🔹 Форма для email */}
          {pickupTime && (
            <div className="email-subscription" style={{ marginTop: '30px' }}>
              <h3>{t('want_to_receive_email')}</h3>
              <p>{t('email_info_text')}</p>

              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t('enter_email')}
                className="transfer-input"
                required
              />

              <div style={{ marginTop: '10px' }}>
                <input
                  type="checkbox"
                  checked={checkboxAccepted}
                  onChange={(e) => setCheckboxAccepted(e.target.checked)}
                  id="consent"
                />
                <label htmlFor="consent" style={{ marginLeft: '8px' }}>
                  {t('consent_text')}
                </label>
              </div>

              <button
                onClick={handleEmailSubmit}
                className="transfer-button"
                style={{ marginTop: '15px' }}
                disabled={!checkboxAccepted || !email}
              >
                {t('send_to_email')}
              </button>

              {emailSentMessage && (
                <p style={{ marginTop: '10px', color: 'green' }}>{emailSentMessage}</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AirportTransferGroupPage;
