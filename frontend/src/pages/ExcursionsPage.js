import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import PageBanner from "../components/PageBanner";
import "../styles/ExcursionsPage.css";

const ExcursionsPage = () => {
  const { t, i18n } = useTranslation();
  const [excursions, setExcursions] = useState([]);
  const [loading, setLoading] = useState(true);

  const defaultImage = "/images/default_excursion.jpg";

  useEffect(() => {
    axios
      .get("/api/excursions/", {
        headers: { "Accept-Language": i18n.language } // ✅ отправляем язык
      })
      .then((response) => {
        setExcursions(response.data || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Ошибка загрузки экскурсий:", error);
        setLoading(false);
      });
  }, [i18n.language]);

  if (loading) return <p>{t("loading")}</p>;
  if (!excursions || excursions.length === 0)
    return <p>{t("no_excursions_found")}</p>;

  const translateDays = (days) => {
    return days.map((day) => t(day));
  };

  return (
    <>
      <PageBanner page="excursions" />

      <div className="page-container">
        <h2 style={{ textAlign: "center", marginBottom: "20px" }}>
          {t("excursions")}
        </h2>

        <div className="excursions-list">
          {excursions.map((excursion) => {
            let imageUrl = defaultImage;
            if (
              excursion &&
              typeof excursion.image === "string" &&
              excursion.image.length > 0
            ) {
              imageUrl = excursion.image.startsWith("http")
                ? excursion.image
                : `http://127.0.0.1:8000${excursion.image}`;
            }

            return (
              <div key={excursion.id} className="excursion-card">
                <img
                  src={imageUrl}
                  alt={excursion.localized_title || t("excursion")}
                  className="excursion-thumb"
                  onError={(e) => (e.target.src = defaultImage)}
                />

                <h2>{excursion.localized_title || t("excursion")}</h2>

                <p>
                  {t("duration")}: {excursion.duration || "?"} {t("hours")}
                </p>

                {excursion.localized_description && (
                  <p
                    className="excursion-description"
                    dangerouslySetInnerHTML={{
                      __html: excursion.localized_description
                    }}
                  />
                )}

                {excursion.days && Array.isArray(excursion.days) ? (
                  <p>
                    {t("excursion_days")}:{" "}
                    {translateDays(excursion.days).join(", ")}
                  </p>
                ) : (
                  <p>{t("excursion_days_not_specified")}</p>
                )}

                <Link to={`/excursions/${excursion.id}`}>
                  {t("read_more")}
                </Link>
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
};

export default ExcursionsPage;
