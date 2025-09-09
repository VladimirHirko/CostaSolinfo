// src/pages/ExcursionDetailPage.js
import React, { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { useTranslation } from "react-i18next";
import PageBanner from "../components/PageBanner";
import PickupMap from "../components/PickupMap";
import "../styles/ExcursionDetailPage.css";
import Breadcrumbs from "../components/Breadcrumbs";
import RulesModal from "../components/RulesModal";
import { fetchExcursionRules } from "../helpers/core";

// ⬇️ NEW: хелперы для подписей дней/языков
import { weekdayShort, langName } from "../utils/excursions";

const ExcursionDetailPage = () => {
  const { id } = useParams();
  const { i18n, t } = useTranslation();

  const [excursion, setExcursion] = useState(null);
  const [hotelQuery, setHotelQuery] = useState("");
  const [hotelOptions, setHotelOptions] = useState([]);
  const [selectedHotel, setSelectedHotel] = useState(null);
  const [pickupInfo, setPickupInfo] = useState(null);
  const [error, setError] = useState("");

  // UI/галерея
  const [modalOpen, setModalOpen] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showArrows, setShowArrows] = useState(false);

  // refs
  const mapRef = useRef(null);
  const hideTimeoutRef = useRef(null);
  const hotelInputRef = useRef(null);

  // Модалка правил поведения на экскурсиях
  const [rulesOpen, setRulesOpen] = useState(false);
  const [rulesHtml, setRulesHtml] = useState("");
  const [rulesTitle, setRulesTitle] = useState(t("rules.title"));

  // ===== Загрузка правил экскурсии по текущему языку =====
  useEffect(() => {
    const lang = (i18n.language || "ru").toLowerCase().split("-")[0];
    fetchExcursionRules(lang)
      .then((d) => {
        setRulesHtml(d?.content || "");
        setRulesTitle(d?.title || t("rules.title"));
      })
      .catch((e) => {
        console.error("Ошибка загрузки правил:", e);
        setRulesHtml("");
      });
  }, [i18n.language, t]);

  // ===== Смена экскурсии — сбросить все выборы/состояния =====
  useEffect(() => {
    setHotelQuery("");
    setHotelOptions([]);
    setSelectedHotel(null);
    setPickupInfo(null);
    setError("");
  }, [id]);

  // ===== Загрузка экскурсии =====
  useEffect(() => {
    let cancelled = false;
    axios
      .get(`/api/excursions/${id}/`, {
        headers: { "Accept-Language": i18n.language },
      })
      .then((res) => {
        if (!cancelled) setExcursion(res.data);
      })
      .catch((err) => console.error("Ошибка загрузки экскурсии:", err));
    return () => {
      cancelled = true;
    };
  }, [id, i18n.language]);

  // ===== Поиск отелей =====
  useEffect(() => {
    if (hotelQuery.length < 2 || selectedHotel?.name === hotelQuery) {
      setHotelOptions([]);
      return;
    }

    const controller = new AbortController();
    const delay = setTimeout(() => {
      axios
        .get(`/api/hotels/?search=${encodeURIComponent(hotelQuery)}`, {
          signal: controller.signal,
        })
        .then((res) => setHotelOptions(res.data))
        .catch((err) => {
          if (err.name !== "CanceledError" && err.name !== "AbortError") {
            setHotelOptions([]);
          }
        });
    }, 300);

    return () => {
      clearTimeout(delay);
      controller.abort();
    };
  }, [hotelQuery, selectedHotel]);

  // ===== Выбор отеля =====
  const handleSelectHotel = (hotel) => {
    setSelectedHotel({
      ...hotel,
      lat: hotel.latitude ? Number(hotel.latitude) : null,
      lng: hotel.longitude ? Number(hotel.longitude) : null,
    });
    setHotelQuery(hotel.name);
    setHotelOptions([]);
    hotelInputRef.current?.blur();

    axios
      .get(`/api/excursions/${id}/pickup/?hotel_id=${hotel.id}`)
      .then((res) => {
        if (res.data && res.data.lat != null && res.data.lng != null) {
          setPickupInfo({
            ...res.data,
            lat: res.data.lat ? Number(res.data.lat) : null,
            lng: res.data.lng ? Number(res.data.lng) : null,
            name: res.data.name || hotel.name,
            time: res.data.time || null,
            adult_price: res.data.price_adult || null,
            child_price: res.data.price_child || null,
          });
          setError("");
        } else {
          setPickupInfo(null);
          setError(t("no_excursion_for_hotel"));
        }
      })
      .catch(() => {
        setPickupInfo(null);
        setError(t("no_excursion_for_hotel"));
      });
  };

  // ===== Мягкий скролл к карте =====
  useEffect(() => {
    if (!pickupInfo) return;
    const tmo = setTimeout(() => {
      mapRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 400);
    return () => clearTimeout(tmo);
  }, [pickupInfo]);

  // ===== Галерея =====
  const handleGalleryTap = () => {
    setShowArrows(true);
    if (hideTimeoutRef.current) clearTimeout(hideTimeoutRef.current);
    hideTimeoutRef.current = setTimeout(() => setShowArrows(false), 3000);
  };
  useEffect(() => () => hideTimeoutRef.current && clearTimeout(hideTimeoutRef.current), []);

  const openModal = (index) => { setCurrentIndex(index); setModalOpen(true); };
  const closeModal = () => setModalOpen(false);
  const prevImage = () => setCurrentIndex((prev) => (prev === 0 ? excursion.images.length - 1 : prev - 1));
  const nextImage = () => setCurrentIndex((prev) => (prev === excursion.images.length - 1 ? 0 : prev + 1));

  if (!excursion) return <p>{t("loading")}</p>;

  return (
    <>
      <PageBanner page="excursions" />
      <div className="page-container">
        <Breadcrumbs
          items={[
            { to: "/", label: t("home") },
            { to: "/excursions", label: t("excursions") },
            { label: excursion?.title || "…" },
          ]}
        />

        <div className="excursion-detail-container">
          <h1>{excursion.localized_title}</h1>

          {/* NEW: Информ-блоки — дни проведения и языки экскурсии */}
          {Array.isArray(excursion.available_days) && excursion.available_days.length > 0 && (
            <div className="x-card-row">
              <span className="x-label">{t("exc.available_on")}:</span>
              <div className="x-chips">
                {excursion.available_days.map((d) => (
                  <span key={d} className="x-chip x-chip--day">{weekdayShort(t, d)}</span>
                ))}
              </div>
            </div>
          )}

          {Array.isArray(excursion.tour_languages) && excursion.tour_languages.length > 0 && (
            <div className="x-card-row">
              <span className="x-label">{t("exc.tour_languages")}:</span>
              <div className="x-chips">
                {excursion.tour_languages.map((code) => (
                  <span key={code} className="x-chip x-chip--lang">{langName(t, code)}</span>
                ))}
              </div>
            </div>
          )}

          {/* Фотогалерея */}
          {excursion.images?.length > 0 && (
            <div
              className={`excursion-gallery-container ${showArrows ? "show-arrows" : ""}`}
              onClick={handleGalleryTap}
            >
              <button
                className="gallery-arrow left"
                onClick={(e) => {
                  e.stopPropagation();
                  document.querySelector(".excursion-gallery")
                    .scrollBy({ left: -300, behavior: "smooth" });
                }}
              >
                ‹
              </button>

              <div className="excursion-gallery">
                {excursion.images.map((img, idx) => (
                  <img
                    key={idx}
                    src={img}
                    alt={`Фото ${idx + 1}`}
                    onClick={(e) => { e.stopPropagation(); openModal(idx); }}
                  />
                ))}
              </div>

              <button
                className="gallery-arrow right"
                onClick={(e) => {
                  e.stopPropagation();
                  document.querySelector(".excursion-gallery")
                    .scrollBy({ left: 300, behavior: "smooth" });
                }}
              >
                ›
              </button>
            </div>
          )}

          {modalOpen && (
            <div className="modal" onClick={closeModal}>
              <span className="close-btn" onClick={closeModal}>×</span>
              <span className="modal-arrow left" onClick={(e) => { e.stopPropagation(); prevImage(); }}>‹</span>
              <img src={excursion.images[currentIndex]} alt={`Фото ${currentIndex + 1}`} />
              <span className="modal-arrow right" onClick={(e) => { e.stopPropagation(); nextImage(); }}>›</span>
            </div>
          )}

          {/* Основной контент */}
          <div className="excursion-content">
            {excursion.content_blocks?.map((block, idx) => {
              const excursionTitle = (excursion.localized_title || excursion.title || "").trim();
              const blockTitle = (block.localized_title || "").trim();
              const isDescription = (block.block_type || block.type) === "description";
              const showTitle = blockTitle && blockTitle !== excursionTitle && !isDescription;

              return (
                <div key={idx} className="excursion-block">
                  {showTitle && <h2>{block.localized_title}</h2>}
                  <div dangerouslySetInnerHTML={{ __html: block.localized_content }} />
                </div>
              );
            })}
          </div>

          <div style={{ margin: "16px 0 24px" }}>
            <button className="btn-primary rules-btn" onClick={() => setRulesOpen(true)} disabled={!rulesHtml}>
              📝 {t("rules.button")}
            </button>
          </div>
          <RulesModal open={rulesOpen} onClose={() => setRulesOpen(false)} html={rulesHtml} title={rulesTitle} okLabel={t("rules.ok")} />

          {/* Блок выбора отеля */}
          <div className="hotel-select-block">
            <h3 className="hotel-title">🚍 {t("excursion.select_hotel_title")}</h3>

            <div className="hotel-select">
              <label htmlFor="hotel-input" className="hotel-label">
                {t("choose_your_hotel")}
              </label>
              <input
                id="hotel-input"
                ref={hotelInputRef}
                type="text"
                value={hotelQuery}
                autoComplete="off"
                onChange={(e) => {
                  setHotelQuery(e.target.value);
                  setSelectedHotel(null);
                }}
                placeholder={t("excursion.select_hotel_placeholder")}
              />
              {hotelOptions.length > 0 && (
                <ul>
                  {hotelOptions.map((hotel) => (
                    <li
                      key={hotel.id}
                      onClick={() => {
                        handleSelectHotel(hotel);
                        setHotelOptions([]);
                        hotelInputRef.current?.blur();
                      }}
                    >
                      {hotel.name}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Карта с точкой сбора */}
          {pickupInfo && (
            <div ref={mapRef} className="pickup-section">
              <div className="pickup-details">
                <p className="pickup-time">
                  ⏰ {t("excursion_pickup_time")}: <span>{pickupInfo.time}</span>
                </p>

                {(pickupInfo.adult_price || pickupInfo.child_price) && (
                  <div className="excursion-prices">
                    {pickupInfo.adult_price && (
                      <p className="price-adult">💶 {t("adult_price")}: {pickupInfo.adult_price} €</p>
                    )}
                    {pickupInfo.child_price && (
                      <>
                        <p className="price-child">👧 {t("child_price")}: {pickupInfo.child_price} €</p>
                        <p className="child-note">{t("excursion.child_free_note")}</p>
                      </>
                    )}
                  </div>
                )}
              </div>

              <h3 className="pickup-title">{t("pickup_point")}</h3>
              <PickupMap hotel={selectedHotel} pickupPoint={pickupInfo} />

              {pickupInfo.lat && pickupInfo.lng && (
                <div className="google-maps-button-container">
                  <a
                    href={`https://www.google.com/maps?q=${pickupInfo.lat},${pickupInfo.lng}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="book-button"
                  >
                    📍 {t("open_in_google_maps")}
                  </a>
                </div>
              )}
            </div>
          )}

          {error && (
            <p style={{ color: "red", textAlign: "center", marginTop: "10px" }}>
              {error}
            </p>
          )}
        </div>
      </div>
    </>
  );
};

export default ExcursionDetailPage;
