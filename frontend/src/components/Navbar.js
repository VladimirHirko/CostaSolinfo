import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../styles/navbar.css';
import { useTranslation } from 'react-i18next';

function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const { t, i18n } = useTranslation();

  const toggleMenu = () => setIsOpen(!isOpen);
  const handleLanguageChange = (event) => i18n.changeLanguage(event.target.value);

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span className="brand-logo">CostaSolinfo</span>

        <div className="navbar-controls">
          <button className="burger" onClick={toggleMenu}>☰</button>
          <div className="lang-wrapper">
            <span className="lang-label">🌐</span>
            <select onChange={handleLanguageChange} value={i18n.language} className="lang-selector">
              <option value="ru">🇷🇺 Рус</option>
              <option value="en">🇬🇧 Eng</option>
              <option value="lt">🇱🇹 Lt</option>
              <option value="lv">🇱🇻 Lv</option>
              <option value="et">🇪🇪 Et</option>
              <option value="uk">🇺🇦 Ua</option>
              <option value="es">🇪🇸 Es</option>
            </select>
          </div>
        </div>
      </div>

      <div className={`navbar-links ${isOpen ? 'active' : ''}`}>
        <Link to="/" onClick={() => setIsOpen(false)}>{t('home')}</Link>
        <Link to="/excursions" onClick={() => setIsOpen(false)}>{t('excursions')}</Link>
        <Link to="/info-meeting" onClick={() => setIsOpen(false)}>{t('info_meeting')}</Link>
        <Link to="/airport-transfer" onClick={() => setIsOpen(false)}>{t('airport_transfer')}</Link>
        <Link to="/ask" onClick={() => setIsOpen(false)}>{t('ask')}</Link>
        <Link to="/contacts" onClick={() => setIsOpen(false)}>{t('contacts')}</Link>
        <Link to="/about" onClick={() => setIsOpen(false)}>{t('about')}</Link>
      </div>
    </nav>
  );
}

export default Navbar;
