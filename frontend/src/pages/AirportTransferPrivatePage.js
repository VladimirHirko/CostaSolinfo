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
  const [transfers, setTransfers] = useState([]);
  const [showInquiryForm, setShowInquiryForm] = useState(false);
  const [lastName, setLastName] = useState('');
  const [needLastName, setNeedLastName] = useState(false);
  const [email, setEmail] = useState('');
  const [checkboxAccepted, setCheckboxAccepted] = useState(false);
  const [emailSentMessage, setEmailSentMessage] = useState('');
  const [inquiryLastName, setInquiryLastName] = useState('');
  const [inquiryHotel, setInquiryHotel] = useState('');
  const [inquiryDate, setInquiryDate] = useState(null);
  const [inquiryFlight, setInquiryFlight] = useState('');
  const [inquiryMessage, setInquiryMessage] = useState('');
  const [inquiryEmail, setInquiryEmail] = useState('');
  const [inquirySuccessMessage, setInquirySuccessMessage] = useState('');
  const [inquiryHotelSuggestions, setInquiryHotelSuggestions] = useState([]);
  const [inquiryHotelId, setInquiryHotelId] = useState(null);
  const [inquirySuggestionsVisible, setInquirySuggestionsVisible] = useState(false);
  const [transferType] = useState('private');
  const [transferLoading, setTransferLoading] = useState(false);
  const [transferResult, setTransferResult] = useState(null);
  const [transferError, setTransferError] = useState('');
  const [selectedHotel, setSelectedHotel] = useState(null);
  const [departureDate, setDepartureDate] = useState('');
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
    setSelectedHotel({ id });
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

    const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
    const dateStr = localDate.toISOString().split('T')[0];
    setDepartureDate(localDate);

    let url = `http://localhost:8000/api/transfer-schedule/?hotel_id=${hotelId}&date=${dateStr}&type=private`;
    if (lastName) {
      url += `&last_name=${encodeURIComponent(lastName.trim())}`;
    }

    try {
      const response = await fetch(url);
      const data = await response.json();

      if (response.ok) {
        if (Array.isArray(data)) {
          if (data.length > 1 && !lastName) {
            // Несколько трансферов — просим фамилию
            setNeedLastName(true);
            setTransfers(data);
            setPickupTime('');
            setPickupPoint('');
            setPickupCoords(null);
            setError(t('please_enter_last_name'));
          } else {
            // Один трансфер или фамилия уже указана
            const item = data[0];
            setPickupTime(item.pickup_time || '');
            setPickupPoint(item.pickup_point || '');
            setPickupCoords({ lat: item.pickup_lat, lng: item.pickup_lng });
            setNeedLastName(false);
            setError('');
          }
        } else if (typeof data === 'object' && data.success) {
          // Успешный точный результат
          setPickupTime(data.pickup_time || '');
          setPickupPoint(data.pickup_point || '');
          setPickupCoords({ lat: data.pickup_lat, lng: data.pickup_lng });
          setNeedLastName(false);
          setError('');
        } else if (data.success === false && data.reason === 'multiple_transfers') {
          setNeedLastName(true);
          setTransfers([]);
          setPickupTime('');
          setPickupPoint('');
          setPickupCoords(null);
          setError(t('please_enter_last_name'));
        } else if (data.success === false && data.reason === 'no_exact_match' && data.suggestion) {
          setError(`${t('did_you_mean')} "${data.suggestion}"?`);
        } else if (data.success === false && data.reason === 'not_found') {
          setError(t('no_transfer_for_lastname'));
          setShowInquiryForm(true);
        } else {
          setError(t('no_transfer_found'));
          setPickupTime('');
          setPickupPoint('');
          setPickupCoords(null);
        }
      } else {
        if (
          data?.detail?.includes('No transfer schedule') ||
          data?.error?.includes('No transfer schedule')
        ) {
          setError(t('no_transfer_schedule_for_this_date'));
          setShowInquiryForm(true);
          setPickupTime('');
          setPickupPoint('');
          setPickupCoords(null);
          return;
        }

        if (data?.error?.includes('No transfer found for this last name')) {
          setError(t('no_transfer_for_lastname'));
          setShowInquiryForm(true);
          return;
        }

        if (data?.error === 'No exact match found' && data?.suggestion) {
          setError(`${t('did_you_mean')} "${data.suggestion}"?`);
          return;
        }

        setError(data?.error || t('something_went_wrong'));
      }
    } catch (err) {
      console.error(err);
      setError(t('something_went_wrong'));
    }
  };




  const handleInquirySubmit = async (e) => {
    e.preventDefault();

    if (!inquiryLastName || !inquiryHotel || !inquiryDate || !inquiryEmail) {
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

  const handleFetchTransfer = async () => {
    setTransferLoading(true);
    setTransferResult(null);
    setTransferError('');

    if (!selectedHotel || !departureDate) {
      setTransferError(t('please_fill_all_fields'));
      setTransferLoading(false);
      return;
    }

    const params = new URLSearchParams({
      hotel_id: selectedHotel.id,
      date: departureDate.toISOString().split('T')[0],
      type: transferType,
    });

    if (lastName.trim() !== '') {
      params.append('last_name', lastName.trim());
    }

    try {
      const response = await fetch(`/api/transfer-schedule/?${params.toString()}`);
      const data = await response.json();

      if (!response.ok) {
        if (data.suggestion) {
          setTransferError(`${t('did_you_mean')}: ${data.suggestion}`);
        } else if (transferType === 'private' && !lastName) {
          setTransferError(t('please_enter_last_name'));
        } else {
          setTransferError(t('no_transfer_found_message'));
        }
      } else {
        setTransferResult(data);
      }
    } catch (error) {
      console.error("Ошибка при получении трансфера:", error);
      setTransferError(t('something_went_wrong'));
    }

    setTransferLoading(false);
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

      {error && (
        <div className="transfer-warning-box">
          {error}
        </div>
      )}


      {needLastName && (
        <div className="transfer-form left-aligned" style={{ marginTop: '20px' }}>
          <label htmlFor="lastNameInput">{t('enter_last_name')}</label>
          <input
            id="lastNameInput"
            type="text"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            placeholder={t('your_last_name')}
            className="transfer-input"
          />
          <button
            onClick={handleSubmit}
            className="transfer-button"
            style={{ marginTop: '15px' }}
          >
            {t('find_my_transfer')}
          </button>
        </div>
      )}

      {error === 'No transfer found for this last name' && (
        <div style={{ marginTop: '30px' }}>
          <p>{t('not_found_contact_us')}</p>
          <button
            className="transfer-button"
            onClick={() => setShowInquiryForm(true)}
          >
            {t('open_contact_form')}
          </button>
        </div>
      )}

      {showInquiryForm && (
        <form
          onSubmit={handleInquirySubmit}
          className="transfer-form left-aligned inquiry-form-animated"
          style={{ marginTop: '20px' }}
        >
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

          <button className="transfer-button" style={{ marginTop: '15px' }}>
            {t('send_request')}
          </button>
        </form>
      )}

      {inquirySuccessMessage && !pickupTime && (
        <div className="success-message-box">
          {inquirySuccessMessage}
        </div>
      )}


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
