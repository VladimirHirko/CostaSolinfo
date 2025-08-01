import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner'; // подключаем общий баннер
import './HomePage.css';

const HomePage = () => {
  const { i18n } = useTranslation();
  const [title, setTitle] = useState('');
  const [subtitle, setSubtitle] = useState('');
  const [bannerImage, setBannerImage] = useState('');

  const defaultImage = '/images/default_excursion.jpg';

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/homepage/')
      .then(res => res.json())
      .then(data => {
        setTitle(data?.[`title_${i18n.language}`] || data?.title || '');
        setSubtitle(data?.[`subtitle_${i18n.language}`] || data?.subtitle || '');

        let imageUrl = defaultImage;
        if (data?.banner_image && typeof data.banner_image === 'string') {
          imageUrl = data.banner_image.startsWith('http')
            ? data.banner_image
            : `http://127.0.0.1:8000${data.banner_image}`;
        }
        setBannerImage(imageUrl);
      })
      .catch(err => {
        console.error('Ошибка загрузки главной страницы:', err);
        setBannerImage(defaultImage);
      });
  }, [i18n.language]);

  return (
    <>
      {/* 🔹 Баннер как на других страницах */}
      <div className="page-banner-wrapper">
        <div
          className="page-banner"
          style={{ backgroundImage: `url(${bannerImage})` }}
        >
          <div className="page-banner-content">{title}</div>
        </div>
      </div>

      {/* 🔹 Контент */}
      <div className="page-container">
        <div
          className="homepage-subtitle"
          dangerouslySetInnerHTML={{ __html: subtitle }}
        />
      </div>
    </>
  );
};

export default HomePage;
