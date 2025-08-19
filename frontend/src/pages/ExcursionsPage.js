// src/pages/ExcursionsPage.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import PageBanner from "../components/PageBanner";
import "../styles/ExcursionsPage.css";
import Breadcrumbs from "../components/Breadcrumbs";

const ExcursionsPage = () => {
  const { t, i18n } = useTranslation();
  const [excursions, setExcursions] = useState([]);
  const [loading, setLoading] = useState(true);

  const defaultImage = "/images/default_excursion.jpg";

  useEffect(() => {
    axios
      .get("/api/excursions/", { headers: { "Accept-Language": i18n.language } })
      .then(res => { setExcursions(res.data || []); })
      .catch(err => { console.error("Ошибка загрузки экскурсий:", err); })
      .finally(() => setLoading(false));
  }, [i18n.language]);

  if (loading) return <p>{t("loading")}</p>;
  if (!excursions || excursions.length === 0) return <p>{t("no_excursions_found")}</p>;

  return (
    <>
      <PageBanner page="excursions" />

      <div className="page-container">
        <Breadcrumbs
          items={[
            { to: "/", label: t("home") },
            { label: t("excursions") },
          ]}
        />

        <h2 style={{ textAlign: "center", marginBottom: 20 }}>
          {t("excursions")}
        </h2>

        <div className="excursions-list">
          {excursions.map((excursion) => {
            let imageUrl = defaultImage;
            if (excursion && typeof excursion.image === "string" && excursion.image.length > 0) {
              imageUrl = excursion.image.startsWith("http")
                ? excursion.image
                : `http://127.0.0.1:8000${excursion.image}`;
            }

            const introText = excursion.localized_description
              ? excursion.localized_description.replace(/<\/?[^>]+(>|$)/g, "").slice(0, 120) + "…"
              : "";

            return (
              <div key={excursion.id} className="excursion-card">
                <img
                  src={imageUrl}
                  alt={excursion.localized_title || t("excursion")}
                  className="excursion-thumb"
                  onError={(e) => { e.currentTarget.src = defaultImage; }}
                />

                <h2>{excursion.localized_title || t("excursion")}</h2>

                {introText && <p className="excursion-intro">{introText}</p>}

                <Link to={`/excursion/${excursion.id}`}>{t("read_more")}</Link>
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
};

export default ExcursionsPage;
