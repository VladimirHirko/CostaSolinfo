import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import './HomePage.css'; // подключаем стили

const HomePage = () => {
  const { i18n } = useTranslation();
  const [title, setTitle] = useState('');
  const [subtitle, setSubtitle] = useState('');
  const [image, setImage] = useState('');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/homepage/')
      .then(res => res.json())
      .then(data => {
        setTitle(data[`title_${i18n.language}`] || data.title);
        setSubtitle(data[`subtitle_${i18n.language}`] || data.subtitle);
        const imageUrl = data.banner_image.startsWith('http')
          ? data.banner_image
          : `http://127.0.0.1:8000${data.banner_image}`; // добавляем домен если нужно

        setImage(imageUrl);
      });
  }, [i18n.language]);

  return (
    <div className="home-page">
      {image && <img src={image} alt="Banner" className="homepage-banner" />}
      <h1 className="homepage-title">{title}</h1>
      
      {/* Рендерим HTML из админки */}
      <div
        className="homepage-subtitle"
        dangerouslySetInnerHTML={{ __html: subtitle }}
      />
    </div>
  );
};

export default HomePage;
