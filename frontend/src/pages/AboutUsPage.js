// frontend/src/pages/AboutUsPage.js
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import { FaEnvelope, FaWhatsapp } from 'react-icons/fa';

import '../styles/main.css';
import '../styles/about.css';

function AboutUsPage() {
  const { t } = useTranslation();
  const [team, setTeam] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/about/team/')
      .then(res => res.json())
      .then(data => setTeam(data))
      .catch(err => console.error('Ошибка загрузки команды:', err));
  }, []);

  return (
    <>
      <PageBanner page="about" />

      <div className="page-container">
        <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>
          {t('about')}
        </h2>

        <p className="welcome-text" style={{ textAlign: 'center' }}>
          {t('about_intro')}
        </p>

        <div className="about-section">
          <h3 style={{ textAlign: 'center' }}>{t('our_team')}</h3>

          <div className="team-grid">
            {team.map((member, index) => (
              <div className="team-card" key={index}>
                <img src={member.photo} alt={member.name} className="team-photo" />
                <h4>{member.name}</h4>
                <p className="team-role">{member.position}</p>

                <div className="team-contact">
                  {member.email && (
                    <a href={`mailto:${member.email}`} title="Email">
                      <FaEnvelope />
                    </a>
                  )}
                  {member.whatsapp && (
                    <a
                      href={`https://wa.me/${member.whatsapp.replace(/\D/g, '')}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      title="WhatsApp"
                    >
                      <FaWhatsapp />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

export default AboutUsPage;
