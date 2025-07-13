// InfoMeetingPage.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import Button from '../components/Button';

const InfoMeetingPage = () => {
  const { t, i18n } = useTranslation();
  const [welcomeText, setWelcomeText] = useState('');
  const [hotels, setHotels] = useState([]);
  const [selectedHotel, setSelectedHotel] = useState(null);
  const [schedule, setSchedule] = useState([]);
  const [error, setError] = useState('');
  const lang = i18n.language;


  // Загрузка текста страницы (на нужном языке)
  useEffect(() => {
    axios.get('/api/info-meeting/')
      .then(res => {
        const data = res.data;
        const localized = data[`content_${i18n.language}`] || data.content || '';
        setWelcomeText(localized);
      })
      .catch(() => setWelcomeText(''));
  }, [i18n.language]);

  // Загрузка списка отелей
  useEffect(() => {
    axios.get('/api/hotels/')
      .then(res => setHotels(res.data))
      .catch(() => setHotels([]));
  }, []);

  const handleSubmit = () => {
    if (!selectedHotel) return;
    axios.get(`/api/info_meetings/?hotel_id=${selectedHotel.id}`)
      .then(res => setSchedule(res.data))
      .catch(() => {
        setSchedule([]);
        setError(t('no_meetings_found'));
      });
  };

  return (
    <>
      <PageBanner page="info_meeting" />

      <div className="page-container">
        <h2 className="mb-3">{t('info_meeting_title')}</h2>

        <div
          className="welcome-text"
          dangerouslySetInnerHTML={{ __html: welcomeText }}
        />

        <div className="info-meeting-form">
          <label htmlFor="hotelSelect">{t('select_hotel')}</label>
          <select
            id="hotelSelect"
            className="info-meeting-select"
            onChange={e => {
              const hotel = hotels.find(h => h.id === parseInt(e.target.value));
              setSelectedHotel(hotel);
            }}
          >
            <option value="">{t('choose_hotel')}</option>
            {hotels.map(hotel => (
              <option key={hotel.id} value={hotel.id}>
                {hotel.name}
              </option>
            ))}
          </select>

          <Button onClick={handleSubmit}>
            {t('check_schedule')}
          </Button>

        </div>

        {schedule.length > 0 ? (
          <table className="table mt-4">
            <thead>
              <tr>
                <th>{t('date')}</th>
                <th>{t('time_from')}</th>
                <th>{t('time_to')}</th>
              </tr>
            </thead>
            <tbody>
              {schedule.map((item, index) => (
                <tr key={index}>
                  <td>{item.date}</td>
                  <td>{item.time_from}</td>
                  <td>{item.time_to}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : error && (
          <div className="error-message mt-4">{error}</div>
        )}
      </div>
    </>
  );
};

export default InfoMeetingPage;
