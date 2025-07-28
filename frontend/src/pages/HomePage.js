import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import './HomePage.css';

const HomePage = () => {
  const { i18n } = useTranslation();
  const [title, setTitle] = useState('');
  const [subtitle, setSubtitle] = useState('');
  const [image, setImage] = useState('');

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
        setImage(imageUrl);
      })
      .catch(err => {
        console.error('Ошибка загрузки главной страницы:', err);
        setImage(defaultImage); // заглушка при ошибке
      });
  }, [i18n.language]);

  return (
    <div className="home-page">
      {image && (
        <img
          src={image}
          alt="Banner"
          className="homepage-banner"
          onError={(e) => (e.target.src = defaultImage)} // fallback если картинка битая
        />
      )}
      <h1 className="homepage-title">{title}</h1>
      <div
        className="homepage-subtitle"
        dangerouslySetInnerHTML={{ __html: subtitle }}
      />
    </div>
  );
};

export default HomePage;
