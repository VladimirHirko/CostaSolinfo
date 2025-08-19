// src/pages/HomePage.jsx
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import './HomePage.css';

const HomePage = () => {
  const { i18n } = useTranslation();
  const [title, setTitle] = useState('');
  const [subtitle, setSubtitle] = useState('');
  const [bannerImage, setBannerImage] = useState('');

  const defaultImage = '/images/default_excursion.jpg';

  useEffect(() => {
    const ctrl = new AbortController();

    fetch('http://127.0.0.1:8000/api/homepage/', {
      headers: { 'Accept-Language': i18n.language },
      signal: ctrl.signal,
      cache: 'no-store',
    })
      .then(res => res.json())
      .then(data => {
        const lang = i18n.language;

        // ✅ сперва локализованные поля (если BaseTranslationSerializer уже выдал их),
        // затем fallbacks на явные *_<lang>, и в конце на русский как запасной
        const resolvedTitle =
          data?.title ??
          data?.[`title_${lang}`] ??
          data?.title_ru ??
          '';

        const resolvedSubtitle =
          data?.subtitle ??
          data?.[`subtitle_${lang}`] ??
          data?.subtitle_ru ??
          '';

        setTitle(resolvedTitle);
        setSubtitle(resolvedSubtitle);

        let imageUrl = defaultImage;
        if (data?.banner_image && typeof data.banner_image === 'string') {
          imageUrl = data.banner_image.startsWith('http')
            ? data.banner_image
            : `http://127.0.0.1:8000${data.banner_image}`;
        }
        setBannerImage(imageUrl);
      })
      .catch(err => {
        if (err.name !== 'AbortError') {
          console.error('Ошибка загрузки главной страницы:', err);
          setBannerImage(defaultImage);
        }
      });

    return () => ctrl.abort();
  }, [i18n.language]);

  return (
    <>
      {/* Баннер как на других страницах (если нужен image из админки — допиши проп imageUrl={bannerImage} в сам компонент PageBanner) */}
      <PageBanner page="home" />

      <div className="page-container">
        {/* Если нужно — можно отрисовать и заголовок */}
        {title && <h1 style={{ marginBottom: 12 }}>{title}</h1>}

        {/* ВАЖНО: рендерим HTML из админки с форматированием */}
        <div
          className="homepage-subtitle"
          dangerouslySetInnerHTML={{ __html: subtitle || '' }}
        />
      </div>
    </>
  );
};

export default HomePage;
