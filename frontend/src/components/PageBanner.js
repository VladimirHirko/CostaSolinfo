// PageBanner.js
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import './PageBanner.css';

function PageBanner({ page }) {
  const [banner, setBanner] = useState(null);
  const { i18n } = useTranslation();

  useEffect(() => {
    fetch(`http://localhost:8000/api/banner/${page}/`)
      .then((res) => res.json())
      .then((data) => {
        if (data && data.titles) {
          setBanner(data);
        } else {
          console.warn("Нет данных баннера или отсутствует titles:", data);
        }
      })
      .catch((error) => console.error("Ошибка загрузки баннера:", error));
  }, [page]);

  if (!banner) return null;

  const backgroundImage = `url(http://localhost:8000${banner.image})`;
  const title = banner.titles[i18n.language] || banner.titles.ru || '';

  return (
    <div className="page-banner-wrapper">
      <div className="page-banner" style={{ backgroundImage }}>
        <div className="page-banner-content">{title}</div>
      </div>
    </div>
  );
}

export default PageBanner;
