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
  const [hotelSuggestions, setHotelSuggestions] = useState([]);
  const [suggestionsVisible, setSuggestionsVisible] = useState(false);
  const [date, setDate] = useState(null);
  const [pickupTime, setPickupTime] = useState('');
  const [pickupPoint, setPickupPoint] = useState('');
  const [pickupCoords, setPickupCoords] = useState(null);
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
  const handleSelectHotel = (name) => {
    setHotel(name);
    setHotelSuggestions([]);
    setSuggestionsVisible(false);
    setTimeout(() => {
      document.activeElement.blur();
    }, 0);
  };

  // 🔹 Отправка формы
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!hotel || !date) {
      setError(t('please_fill_all_fields'));
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/api/transfer-schedule/?hotel=${encodeURIComponent(
          hotel
        )}&date=${date.toISOString().split('T')[0]}`
      );
      const data = await response.json();
      setPickupTime(data.pickup_time || '');
      setPickupPoint(data.pickup_point || '');
      setPickupCoords({ lat: data.pickup_lat, lng: data.pickup_lng });
      setError('');
    } catch (err) {
      console.error(err);
      setError(t('something_went_wrong'));
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
                <li key={item.id} onMouseDown={() => handleSelectHotel(item.name)}>
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
        </div>
      )}
    </div>
  );
};

export default AirportTransferGroupPage;
