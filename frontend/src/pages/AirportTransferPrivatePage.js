// frontend/src/pages/AirportTransferPrivatePage.js
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import DatePicker from 'react-datepicker';
import TransferMap from '../components/TransferMap';
import 'react-datepicker/dist/react-datepicker.css';

const AirportTransferPrivatePage = () => {
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

  const handleSelectHotel = (name, id) => {
    setHotel(name);
    setHotelId(id);
    setHotelSuggestions([]);
    setSuggestionsVisible(false);
    setTimeout(() => document.activeElement.blur(), 0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!hotelId || !date) {
      setError(t('please_fill_all_fields'));
      return;
    }

    try {
      const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
      const dateStr = localDate.toISOString().split('T')[0];

      const url = `http://localhost:8000/api/transfer-schedule/?hotel_id=${hotelId}&date=${dateStr}&type=private`;

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
          hotel: hotelId,
          transfer_type: 'private',
          departure_date: dateStr,
          language: 'ru'
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
      <PageBanner page="private_transfer" />
      <h1>{t('private_transfer')}</h1>
      <p>{t('enter_hotel_and_date')}</p>

      <form onSubmit={handleSubmit} className="transfer-form left-aligned">
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

        <label>{t('select_date')}</label>
        <DatePicker
          selected={date}
          onChange={(date) => setDate(date)}
          placeholderText={t('select_date')}
          className="transfer-input"
          dateFormat="yyyy-MM-dd"
        />

        <button type="submit" className="transfer-button">
          {t('show_transfer_time')}
        </button>
      </form>

      {error && <p className="error-message">{error}</p>}

      {pickupTime && (
        <div className="transfer-result">
          <h3>{t('pickup_time')}:</h3>
          <p>{pickupTime}</p>
          {pickupPoint && <p>{t('pickup_point')}: {pickupPoint}</p>}

          {pickupCoords && (
            <div style={{ height: '400px', marginTop: '20px' }}>
              <TransferMap lat={pickupCoords.lat} lng={pickupCoords.lng} pickupName={pickupPoint} />
            </div>
          )}

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

export default AirportTransferPrivatePage;
