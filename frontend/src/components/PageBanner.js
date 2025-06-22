import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import './PageBanner.css'; // подключи если еще не подключал

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
  const title =
    banner && banner.titles && (banner.titles[i18n.language] || banner.titles.ru || '');

  return (
    <div className="page-container">
      <div
        className="page-banner"
        style={{
          backgroundImage,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          padding: '80px 20px',
          color: '#fff',
          textAlign: 'center',
          borderRadius: '12px',
          marginBottom: '30px',
          fontWeight: 'bold',
          fontSize: '32px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
        }}
      >
        {title}
      </div>
    </div>
  );
}

export default PageBanner;
