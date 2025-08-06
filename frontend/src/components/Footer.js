import React from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import "../styles/Footer.css";

const Footer = () => {
  const { t } = useTranslation();

  const year = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">
        {/* Левая часть: логотип и название */}
        <div className="footer-left">
          <h2 className="footer-logo">CostaSolinfo</h2>
          <p className="footer-slogan">
            Ваш гид по Коста дель Соль
          </p>
        </div>

        {/* Средняя часть: ссылки */}
        <div className="footer-links">
          <h4>Навигация</h4>
          <ul>
            <li><a href="/">Главная</a></li>
            <li><a href="/excursions">Экскурсии</a></li>
            <li><a href="/info-meeting">Инфо встреча</a></li>
            <li><a href="/airport-transfer">Трансфер</a></li>
            <li><a href="/contacts">Контакты</a></li>
            <li><a href="/about">О нас</a></li>
          </ul>
        </div>

        {/* Правая часть: контакты + соцсети */}
        <div className="footer-right">
          <h4>Контакты</h4>
          <p>Email: <a href="mailto:CostaSolinfo.Malaga@gmail.com">
            CostaSolinfo.Malaga@gmail.com</a>
          </p>
          <p>WhatsApp: <a href="https://wa.me/34660535089">+34 660 535 089</a></p>

          <div className="footer-socials">
            <a href="https://facebook.com" target="_blank" rel="noreferrer">
              <i className="fab fa-facebook"></i>
            </a>
            <a href="https://instagram.com" target="_blank" rel="noreferrer">
              <i className="fab fa-instagram"></i>
            </a>
            <a href="https://wa.me/34660535089" target="_blank" rel="noreferrer">
              <i className="fab fa-whatsapp"></i>
            </a>
          </div>
        </div>
      </div>

      {/* Нижняя полоса */}
      <div className="footer-bottom">
        <p>© {new Date().getFullYear()} CostaSolinfo. Все права защищены.</p>
      </div>
    </footer>
  );
};

export default Footer;
