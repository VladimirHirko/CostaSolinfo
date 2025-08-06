import React, { useState } from 'react';
import '../styles/navbar.css';
import logo from '../assets/logo_CostaSolinfo.PNG';
import { useTranslation } from 'react-i18next';
import { NavLink, Link } from 'react-router-dom';

function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const { t, i18n } = useTranslation();

  const toggleMenu = () => setIsOpen(!isOpen);
  const handleLanguageChange = (event) => i18n.changeLanguage(event.target.value);

  return (
    <nav className={`navbar ${isOpen ? 'active' : ''}`}>

      <div className="navbar-brand">
        <Link to="/" className="navbar-logo-link">
          <img src={logo} alt="CostaSolinfo" className="navbar-logo" />
        </Link>

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
        <NavLink
          to="/"
          className={({ isActive }) => isActive ? 'active' : ''}
          onClick={() => setIsOpen(false)}
        >
          {t('home')}
        </NavLink>

        <NavLink
          to="/excursions"
          className={({ isActive }) => isActive ? 'active' : ''}
          onClick={() => setIsOpen(false)}
        >
          {t('excursions')}
        </NavLink>

        <NavLink
          to="/info-meeting"
          className={({ isActive }) => isActive ? 'active' : ''}
          onClick={() => setIsOpen(false)}
        >
          {t('info_meeting')}
        </NavLink>

        <NavLink
          to="/airport-transfer"
          className={({ isActive }) => isActive ? 'active' : ''}
          onClick={() => setIsOpen(false)}
        >
          {t('airport_transfer')}
        </NavLink>

        <NavLink
          to="/ask"
          className={({ isActive }) => isActive ? 'active' : ''}
          onClick={() => setIsOpen(false)}
        >
          {t('ask')}
        </NavLink>

        <NavLink
          to="/contacts"
          className={({ isActive }) => isActive ? 'active' : ''}
          onClick={() => setIsOpen(false)}
        >
          {t('contacts')}
        </NavLink>

        <NavLink
          to="/about"
          className={({ isActive }) => isActive ? 'active' : ''}
          onClick={() => setIsOpen(false)}
        >
          {t('about')}
        </NavLink>
      </div>

    </nav>
  );
}

export default Navbar;
