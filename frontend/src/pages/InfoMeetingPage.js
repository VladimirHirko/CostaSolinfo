import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import Button from '../components/Button';

const InfoMeetingPage = () => {
  const { t, i18n } = useTranslation();
  const [welcomeText, setWelcomeText] = useState('');
  const [hotelQuery, setHotelQuery] = useState('');
  const [hotelOptions, setHotelOptions] = useState([]);
  const [selectedHotel, setSelectedHotel] = useState(null);
  const [suggestionsVisible, setSuggestionsVisible] = useState(false);
  const [schedule, setSchedule] = useState([]);
  const [error, setError] = useState('');

  // 🔹 Загрузка текста страницы
  useEffect(() => {
    axios.get('/api/info-meeting/')
      .then(res => {
        const data = res.data;
        const localized = data[`content_${i18n.language}`] || data.content || '';
        setWelcomeText(localized);
      })
      .catch(() => setWelcomeText(''));
  }, [i18n.language]);

  // 🔹 Загрузка отелей по поиску
  useEffect(() => {
    if (hotelQuery.length < 2) {
      setHotelOptions([]);
      setSuggestionsVisible(false);
      return;
    }

    const timeout = setTimeout(() => {
      axios.get(`/api/hotels/?search=${hotelQuery}`)
        .then(res => {
          setHotelOptions(res.data);
          setSuggestionsVisible(true);
        })
        .catch(() => {
          setHotelOptions([]);
          setSuggestionsVisible(false);
        });
    }, 300);

    return () => clearTimeout(timeout);
  }, [hotelQuery]);

  // 🔹 Отправка запроса на расписание
  const handleSubmit = () => {
    if (!selectedHotel) return;

    axios.get(`/api/info-meetings/?hotel_id=${selectedHotel.id}`)
      .then(res => {
        const scheduleList = res.data.schedule;
        setSchedule(scheduleList);
        setError(scheduleList.length === 0 ? t('no_meetings_found') : '');
      })
      .catch(() => {
        setSchedule([]);
        setError(t('no_meetings_found'));
      });
  };

  // 🔹 Выбор отеля из подсказки
  const handleSelectHotel = (hotel) => {
    setSelectedHotel(hotel);
    setHotelQuery(hotel.name);
    setHotelOptions([]);
    setSuggestionsVisible(false);
    setTimeout(() => document.activeElement.blur(), 0); // снимаем фокус
  };

  return (
    <>
      <PageBanner page="info_meeting" />

      <div className="page-container">
        

        <div
          className="welcome-text"
          dangerouslySetInnerHTML={{ __html: welcomeText }}
        />

        <div className="info-meeting-form">
          <label htmlFor="hotelInput">{t('select_hotel')}</label>

          <div className="autocomplete-wrapper">
            <input
              id="hotelInput"
              className="transfer-input"
              type="text"
              value={hotelQuery}
              onChange={(e) => {
                setHotelQuery(e.target.value);
                setSelectedHotel(null);
              }}
              placeholder={t('choose_hotel')}
            />
            {suggestionsVisible && hotelOptions.length > 0 && !hotelOptions.some(h => h.name === hotelQuery) && (
              <ul className="autocomplete-list">
                {hotelOptions.map(hotel => (
                  <li key={hotel.id} onMouseDown={() => handleSelectHotel(hotel)}>
                    {hotel.name}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
            <Button onClick={handleSubmit} className="transfer-button">
              {t('check_schedule')}
            </Button>
          </div>
        </div>

        {schedule.length > 0 ? (
          <table className="schedule-table">
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
          <div className="error-message mt-4" style={{ textAlign: 'center', color: 'red' }}>
            {error}
          </div>
        )}
      </div>
    </>
  );
};

export default InfoMeetingPage;
