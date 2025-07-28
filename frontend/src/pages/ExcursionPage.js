// ExcursionsPage.js
import PageBanner from '../components/PageBanner';

import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { useTranslation } from "react-i18next";
import "../styles/ExcursionPage.css";


const ExcursionPage = () => {
  const { id } = useParams();
  const { i18n } = useTranslation();
  const [excursion, setExcursion] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios
      .get(`/api/excursions/${id}/`)
      .then((response) => {
        setExcursion(response.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Ошибка загрузки экскурсии:", error);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <p>Загрузка...</p>;
  if (!excursion) return <p>Экскурсия не найдена</p>;

  const lang = i18n.language || "ru";

  return (
    <div className="excursion-page">
      <h1>{excursion[`title_${lang}`] || excursion.title}</h1>
      {excursion.image && (
        <img
          src={excursion.image}
          alt={excursion.title}
          className="excursion-image"
        />
      )}
      <p>Продолжительность: {excursion.duration} часов</p>
      <p>Дни проведения: {excursion.days.join(", ")}</p>

      <div className="excursion-content">
        {excursion.content_blocks.map((block) => (
          <div key={block.order} className="excursion-block">
            <h2>{block[`title_${lang}`]}</h2>
            <div
              dangerouslySetInnerHTML={{
                __html: block[`content_${lang}`] || "",
              }}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExcursionPage;
