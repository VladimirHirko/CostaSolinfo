import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import "../styles/ExcursionsPage.css";

const ExcursionsPage = () => {
  const { i18n } = useTranslation();
  const [excursions, setExcursions] = useState([]);
  const [loading, setLoading] = useState(true);

  const defaultImage = "/images/default_excursion.jpg";

  useEffect(() => {
    axios
      .get("/api/excursions/")
      .then((response) => {
        setExcursions(response.data || []); // защита от null
        setLoading(false);
      })
      .catch((error) => {
        console.error("Ошибка загрузки экскурсий:", error);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Загрузка...</p>;
  if (!excursions || excursions.length === 0)
    return <p>Экскурсии не найдены</p>;

  const lang = i18n.language || "ru";

  return (
    <div className="excursions-list">
      {excursions.map((excursion) => {
        const lang = i18n.language || "ru";

        // ✅ Безопасное определение URL
        let imageUrl = defaultImage;
        if (excursion && typeof excursion.image === "string" && excursion.image.length > 0) {
          if (excursion.image.startsWith("http")) {
            imageUrl = excursion.image;
          } else {
            imageUrl = `http://127.0.0.1:8000${excursion.image}`;
          }
        }

        return (
          <div key={excursion.id} className="excursion-card">
            <img
              src={imageUrl}
              alt={excursion[`title_${lang}`] || excursion.title || "Экскурсия"}
              className="excursion-thumb"
              onError={(e) => (e.target.src = defaultImage)} // fallback при ошибке загрузки
            />
            <h2>{excursion[`title_${lang}`] || excursion.title}</h2>
            <p>Продолжительность: {excursion.duration || "?"} ч.</p>
            {excursion.days && Array.isArray(excursion.days) ? (
              <p>Дни проведения: {excursion.days.join(", ")}</p>
            ) : (
              <p>Дни проведения: не указаны</p>
            )}
            <Link to={`/excursions/${excursion.id}`}>Подробнее</Link>
          </div>
        );
      })}


    </div>
  );
};

export default ExcursionsPage;
