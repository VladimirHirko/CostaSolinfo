import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { useTranslation } from "react-i18next";
import PageBanner from "../components/PageBanner";
import PickupMap from "../components/PickupMap";
import "../styles/ExcursionDetailPage.css";

const ExcursionDetailPage = () => {
  const { id } = useParams();
  const { i18n, t } = useTranslation();
  const [excursion, setExcursion] = useState(null);
  const [hotelQuery, setHotelQuery] = useState("");
  const [hotelOptions, setHotelOptions] = useState([]);
  const [selectedHotel, setSelectedHotel] = useState(null);
  const [pickupInfo, setPickupInfo] = useState(null);
  const [error, setError] = useState("");

  // Загружаем экскурсию
  useEffect(() => {
    axios
      .get(`/api/excursions/${id}/`, {
        headers: { "Accept-Language": i18n.language },
      })
      .then((res) => setExcursion(res.data))
      .catch((err) => console.error("Ошибка загрузки экскурсии:", err));
  }, [id, i18n.language]);

  // Поиск отелей
  useEffect(() => {
    if (hotelQuery.length < 2) {
      setHotelOptions([]);
      return;
    }

    const delayDebounce = setTimeout(() => {
      axios
        .get(`/api/hotels/?search=${hotelQuery}`)
        .then((res) => setHotelOptions(res.data))
        .catch(() => setHotelOptions([]));
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [hotelQuery]);

  // Выбор отеля
  const handleSelectHotel = (hotel) => {
    setSelectedHotel(hotel);
    setHotelQuery(hotel.name);
    setHotelOptions([]);

    axios
      .get(`/api/excursions/${id}/pickup/?hotel_id=${hotel.id}`)
      .then((res) => {
        if (res.data && res.data.lat && res.data.lng) {
          setPickupInfo(res.data);
          setError("");
        } else {
          setPickupInfo(null);
          setError(t("no_transfer_schedule_for_this_date"));
        }
      })
      .catch(() => {
        setPickupInfo(null);
        setError(t("something_went_wrong"));
      });
  };

  if (!excursion) return <p>{t("loading")}</p>;

  return (
    <>
      <PageBanner page="excursions" />

      <div className="excursion-detail-container">
        <h1>{excursion.localized_title}</h1>

        <div className="excursion-content">
          {excursion.content_blocks?.map((block, idx) => (
            <div key={idx} className="excursion-block">
              <h2>{block.localized_title}</h2>
              <div dangerouslySetInnerHTML={{ __html: block.localized_content }} />
            </div>
          ))}
        </div>


        {/* Фотогалерея */}
        <div className="excursion-gallery">
          {excursion.images?.map((img, idx) => (
            <img key={idx} src={img} alt={`Фото ${idx + 1}`} />
          ))}
        </div>

        {/* Выбор отеля */}
        <div className="hotel-select">
          <label>{t("your_hotel")}</label>
          <input
            type="text"
            value={hotelQuery}
            onChange={(e) => {
              setHotelQuery(e.target.value);
              setSelectedHotel(null);
              setPickupInfo(null);
            }}
            placeholder={t("choose_hotel")}
          />
          <ul>
            {hotelOptions.map((hotel) => (
              <li key={hotel.id} onClick={() => handleSelectHotel(hotel)}>
                {hotel.name}
              </li>
            ))}
          </ul>
        </div>

        {/* Карта с точкой сбора */}
        {pickupInfo && (
          <div>
            <h3>{t("pickup_point")}</h3>
            <PickupMap hotel={selectedHotel} pickupPoint={pickupInfo} />
            <p>
              {t("pickup_time")}: {pickupInfo.time}
            </p>
          </div>
        )}

        {/* Сообщение об ошибке */}
        {error && (
          <p style={{ color: "red", textAlign: "center", marginTop: "10px" }}>
            {error}
          </p>
        )}

        <button className="book-button">{t("book_now")}</button>
      </div>
    </>
  );
};

export default ExcursionDetailPage;
