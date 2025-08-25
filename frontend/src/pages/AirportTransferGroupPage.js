// frontend/src/pages/AirportTransferGroupPage.js
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import DatePicker from 'react-datepicker';
import TransferMap from '../components/TransferMap';
import PrivacyPolicyModal from '../components/PrivacyPolicyModal';
import 'react-datepicker/dist/react-datepicker.css';
import Button from '../components/Button';
import TransferContent from '../components/TransferContent';
import Breadcrumbs from "../components/Breadcrumbs";

const getIsoDate = (d) => {
  const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
  return local.toISOString().split('T')[0];
};

const textFromApi = (t, data) =>
  t(data?.message_key || data?.error_key || 'something_went_wrong');


const AirportTransferGroupPage = () => {
  const { t, i18n } = useTranslation();
  const [hotel, setHotel] = useState('');
  const [hotelId, setHotelId] = useState(null);
  const [hotelSuggestions, setHotelSuggestions] = useState([]);
  const [suggestionsVisible, setSuggestionsVisible] = useState(false);
  const [date, setDate] = useState(null);
  const [pickupTime, setPickupTime] = useState('');
  const [pickupPoint, setPickupPoint] = useState('');
  const [pickupCoords, setPickupCoords] = useState(null);

  const [showInquiryForm, setShowInquiryForm] = useState(false);
  const [inquiryLastName, setInquiryLastName] = useState('');
  const [inquiryHotel, setInquiryHotel] = useState('');
  const [inquiryDate, setInquiryDate] = useState(null);
  const [inquiryFlight, setInquiryFlight] = useState('');
  const [inquiryMessage, setInquiryMessage] = useState('');
  const [inquiryEmail, setInquiryEmail] = useState('');
  const [inquirySuccessMessage, setInquirySuccessMessage] = useState('');
  const [inquiryError, setInquiryError] = useState('');
  const [inquiryHotelSuggestions, setInquiryHotelSuggestions] = useState([]);
  const [inquiryHotelId, setInquiryHotelId] = useState(null);
  const [inquirySuggestionsVisible, setInquirySuggestionsVisible] = useState(false);

  const [email, setEmail] = useState('');
  const [subscriberLastName, setSubscriberLastName] = useState('');
  const [checkboxAccepted, setCheckboxAccepted] = useState(false);
  const [emailSentMessage, setEmailSentMessage] = useState('');
  const [showPolicyModal, setShowPolicyModal] = useState(false);

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
    setInquirySuccessMessage('');
    setInquiryError('');

    if (!hotelId || !date) {
      setError(t('please_fill_all_fields'));
      return;
    }

    try {
      const dateStr = getIsoDate(date);
      const url = `http://localhost:8000/api/transfer-schedule/?hotel_id=${hotelId}&date=${dateStr}&type=group`;

      const response = await fetch(url);
      const data = await response.json();

      if (response.ok) {
        // время ещё не назначено
        if (data?.success === false && data?.reason === 'time_pending') {
          setPickupTime('');
          setPickupPoint(data.pickup_point || '');
          setPickupCoords(
            data.pickup_lat && data.pickup_lng ? { lat: data.pickup_lat, lng: data.pickup_lng } : null
          );
          setShowInquiryForm(true);                  // ← показываем форму
          setError(textFromApi(t, data));            // текст по ключу
          return;
        }

        // успешный ответ
        if (data?.success === true) {
          setPickupTime(data.pickup_time || '');
          setPickupPoint(data.pickup_point || '');
          setPickupCoords(
            data.pickup_lat && data.pickup_lng ? { lat: data.pickup_lat, lng: data.pickup_lng } : null
          );
          setError('');
          setShowInquiryForm(false);
          return;
        }

        // fallback
        setPickupTime('');
        setPickupPoint('');
        setPickupCoords(null);
        setShowInquiryForm(true);
        setError(textFromApi(t, data));
        return;
      }

      // НЕ ok (404/400/…)
      setPickupTime('');
      setPickupPoint('');
      setPickupCoords(null);

      if (data?.error_key || data?.message_key) {
        setError(textFromApi(t, data));
        if (data?.error_key === 'no_transfer_found' || data?.message_key === 'no_transfer_found') {
          setShowInquiryForm(true);
        }
      } else if (typeof data?.error === 'string' && data.error.toLowerCase().includes('no transfer')) {
        setError(t('no_transfer_found_message'));
        setShowInquiryForm(true);
      } else {
        setError(t('something_went_wrong'));
      }
    } catch (err) {
      console.error(err);
      setError(t('something_went_wrong'));
    }
  };


  const handleInquirySubmit = async (e) => {
    e.preventDefault();

    if (!inquiryLastName || !inquiryHotelId || !inquiryDate || !inquiryEmail) {
      setError(t('please_fill_all_fields'));
      return;
    }

    try {
      const localDate = new Date(inquiryDate.getTime() - inquiryDate.getTimezoneOffset() * 60000);
      const dateStr = localDate.toISOString().split('T')[0];

      const response = await fetch('http://localhost:8000/api/transfer-inquiries/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          last_name: inquiryLastName.trim(),
          hotel: inquiryHotelId,
          departure_date: dateStr,
          flight_number: inquiryFlight.trim(),
          message: inquiryMessage.trim(),
          email: inquiryEmail.trim(),
          language: i18n.language, // ⬅️ ВАЖНО: добавляем текущий язык
        }),
      });

      if (response.ok) {
        setInquirySuccessMessage(t('request_sent_successfully'));

        setInquiryLastName('');
        setInquiryHotel('');
        setInquiryDate(null);
        setInquiryFlight('');
        setInquiryMessage('');
        setInquiryEmail('');
        setError('');
        setShowInquiryForm(false);
      } else {
        const data = await response.json();
        console.error('Ошибка запроса:', data);
        setError(t('request_error'));
      }
    } catch (err) {
      console.error('Ошибка соединения:', err);
      setError(t('request_error'));
    }
  };

  useEffect(() => {
    if (inquiryHotel.length >= 2) {
      fetch(`http://localhost:8000/api/hotels/?search=${inquiryHotel}`)
        .then((res) => res.json())
        .then((data) => {
          setInquiryHotelSuggestions(data);
          setInquirySuggestionsVisible(true);
        })
        .catch((err) => console.error('Ошибка загрузки отелей для запроса:', err));
    } else {
      setInquiryHotelSuggestions([]);
      setInquirySuggestionsVisible(false);
    }
  }, [inquiryHotel]);

  const handleSelectInquiryHotel = (name, id) => {
    setInquiryHotel(name);
    setInquiryHotelId(id);
    setInquiryHotelSuggestions([]);
    setInquirySuggestionsVisible(false);
    setTimeout(() => document.activeElement.blur(), 0);
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
          language: i18n.language,
          last_name: subscriberLastName.trim(), // ⬅️ добавили фамилию
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

  const isValidEmail = (email) =>
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);





  return (
    <>
      <PageBanner page="group_transfer" />
        

      
      <div className="page-container">

      <Breadcrumbs items={[
          { to: "/", label: t("home") },
          { to: "/airport-transfer", label: t("airport_transfer") },
          { label: t("group_transfer") } // или t("private_transfer")
        ]}/>

      <TransferContent page="transfer_group" />
        
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
          <button
            type="submit"
            className="transfer-button"
            style={{ alignSelf: "flex-start" }}
          >
            {t('show_transfer_time')}
          </button>

        </form>

        {/* 🔹 Ошибка */}
        {error && (
          <div className="transfer-warning-box">
            {error}
          </div>
        )}

        {inquirySuccessMessage && !pickupTime && (
          <div className="success-message-box">
            {inquirySuccessMessage}
          </div>
        )}

        {showInquiryForm && (
          <form onSubmit={handleInquirySubmit} className="transfer-form left-aligned" style={{ marginTop: '30px' }}>
            <h3>{t('not_found_contact_us')}</h3>

            {/* для групповых фамилия не обязательна — можешь убрать это поле */}
            <label>{t('your_last_name')}</label>
            <input
              type="text"
              value={inquiryLastName}
              onChange={(e) => setInquiryLastName(e.target.value)}
              className="transfer-input"
            />

            <label>{t('your_hotel')}</label>
            <div className="autocomplete-wrapper">
              <input
                type="text"
                value={inquiryHotel}
                onChange={(e) => setInquiryHotel(e.target.value)}
                placeholder={t('your_hotel')}
                className="transfer-input"
              />
              {inquiryHotelSuggestions.length > 0 && !inquiryHotelSuggestions.some(h => h.name === inquiryHotel) && (
                <ul className="autocomplete-list">
                  {inquiryHotelSuggestions.map((item) => (
                    <li key={item.id} onMouseDown={() => handleSelectInquiryHotel(item.name, item.id)}>
                      {item.name}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <label>{t('departure_date')}</label>
            <DatePicker
              selected={inquiryDate}
              onChange={(date) => setInquiryDate(date)}
              placeholderText={t('select_date')}
              className="transfer-input"
              dateFormat="yyyy-MM-dd"
            />

            <label>{t('flight_number')}</label>
            <input
              type="text"
              value={inquiryFlight}
              onChange={(e) => setInquiryFlight(e.target.value)}
              className="transfer-input"
            />

            <label>{t('question')}</label>
            <textarea
              value={inquiryMessage}
              onChange={(e) => setInquiryMessage(e.target.value)}
              className="transfer-input"
            />

            <label>{t('your_email')}</label>
            <input
              type="email"
              value={inquiryEmail}
              onChange={(e) => setInquiryEmail(e.target.value)}
              className="transfer-input"
            />

            <Button className="transfer-button" style={{ marginTop: '15px' }}>
              {t('send_request')}
            </Button>
          </form>
        )}

        
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

            {inquirySuccessMessage && (
              <p style={{ marginTop: '15px', color: 'green' }}>{inquirySuccessMessage}</p>
            )}
            {inquiryError && (
              <p style={{ marginTop: '15px', color: 'red' }}>{inquiryError}</p>
            )}


            {/* 🔹 Форма для email */}
            {pickupTime && (
              <div className="email-subscription" style={{ marginTop: '30px' }}>
                <h3>{t('want_to_receive_email')}</h3>
                <p>{t('email_info_text')}</p>

                {/* 📨 Email */}
                <div style={{ maxWidth: '320px', margin: '0 auto', textAlign: 'left' }}>
                  <label
                    style={{
                      fontWeight: 'bold',
                      display: 'block',
                      marginBottom: '6px'
                    }}
                  >
                    {t('enter_your_email_label')}
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={t('enter_email')}
                    className="transfer-input"
                    required
                  />
                </div>

                {/* 👤 Фамилия */}
                <div style={{ maxWidth: '320px', margin: '15px auto 0', textAlign: 'left' }}>
                  <label
                    style={{
                      fontWeight: 'bold',
                      display: 'block',
                      marginBottom: '6px'
                    }}
                  >
                    {t('enter_your_lastname_label')}
                  </label>
                  <input
                    type="text"
                    value={subscriberLastName}
                    onChange={(e) => setSubscriberLastName(e.target.value)}
                    placeholder={t('your_last_name')}
                    className="transfer-input"
                    required
                  />
                </div>

                {/* ✅ Checkbox */}
                <div style={{ marginTop: '10px' }}>
                  <input
                    type="checkbox"
                    checked={checkboxAccepted}
                    onChange={(e) => setCheckboxAccepted(e.target.checked)}
                    id="consent"
                    onClick={(e) => e.stopPropagation()} // не даёт всплытию перейти к label
                  />
                  <label
                    htmlFor="consent"
                    style={{ marginLeft: '8px', cursor: 'pointer' }}
                    onClick={() => setShowPolicyModal(true)}
                  >
                    {t('i_agree_with')}{' '}
                    <span style={{ color: 'blue', textDecoration: 'underline' }}>
                      {t('terms_and_privacy')}
                    </span>
                  </label>
                </div>

                <PrivacyPolicyModal
                  isOpen={showPolicyModal}
                  onClose={() => setShowPolicyModal(false)}
                />

                {/* 📩 Кнопка */}
                <Button
                  onClick={handleEmailSubmit}
                  className="transfer-button"
                  style={{
                    marginTop: '20px',
                    backgroundColor: (!checkboxAccepted || !isValidEmail(email) || !subscriberLastName) ? '#ccc' : '#00aaff',
                    color: 'white',
                    border: 'none',
                    padding: '10px 20px',
                    borderRadius: '6px',
                    fontSize: '16px',
                    cursor: (!checkboxAccepted || !isValidEmail(email) || !subscriberLastName) ? 'not-allowed' : 'pointer',
                    transition: '0.3s ease',
                  }}
                  disabled={!checkboxAccepted || !isValidEmail(email) || !subscriberLastName}
                >
                  {t('send_to_email')}
                </Button>


                {emailSentMessage && (
                  <p style={{ marginTop: '10px', color: 'green' }}>{emailSentMessage}</p>
                )}
              </div>
            )}

          </div>
        )}
      </div>
    </>
  );
};

export default AirportTransferGroupPage;