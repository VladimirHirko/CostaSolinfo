import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import MapComponent from '../components/MapComponent';

const AirportTransferPage = () => {
  const { t, i18n } = useTranslation();

  const [transferType, setTransferType] = useState('group');
  const [hotelId, setHotelId] = useState('');
  const [departureDate, setDepartureDate] = useState(null);
  const [lastName, setLastName] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);

    const body = {
      transfer_type: transferType,
      hotel_id: parseInt(hotelId),
      departure_date: departureDate?.toISOString().split('T')[0],
      passenger_last_name: transferType === 'private' ? lastName : '',
    };

    try {
      const response = await fetch('/api/transfer-schedule/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        const err = await response.json();
        setError(err.error || 'Transfer not found');
      }
    } catch (err) {
      setError('Ошибка соединения с сервером');
    }
  };

  return (
    <div className="page">
      <h1>Трансфер в аэропорт</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>
            <input type="radio" value="group" checked={transferType === 'group'} onChange={() => setTransferType('group')} />
            Групповой трансфер
          </label>
          <label>
            <input type="radio" value="private" checked={transferType === 'private'} onChange={() => setTransferType('private')} />
            Индивидуальный трансфер
          </label>
        </div>

        <div>
          <label>Отель (ID):</label>
          <input type="number" value={hotelId} onChange={(e) => setHotelId(e.target.value)} required />
        </div>

        <div>
          <label>Дата вылета:</label>
          <DatePicker
            selected={departureDate}
            onChange={(date) => setDepartureDate(date)}
            dateFormat="yyyy-MM-dd"
            placeholderText="Выберите дату"
          />
        </div>

        {transferType === 'private' && (
          <div>
            <label>Фамилия:</label>
            <input type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} />
          </div>
        )}

        <button type="submit">Показать трансфер</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {result && (
        <div style={{ marginTop: '20px' }}>
          <h3>Информация о трансфере:</h3>
          <p><strong>Время выезда:</strong> {result.departure_time}</p>
          <p><strong>Точка сбора:</strong> {result.pickup_point_name}</p>

          {result.pickup_point_lat && result.pickup_point_lng && (
            <MapComponent lat={result.pickup_point_lat} lng={result.pickup_point_lng} />
          )}
        </div>
      )}
    </div>
  );
};

export default AirportTransferPage;
