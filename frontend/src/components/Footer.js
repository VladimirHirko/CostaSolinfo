import React from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import "../styles/Footer.css";

const Footer = () => {
  const { t } = useTranslation();
  const year = new Date().getFullYear();

  // Заголовки/подписи с безопасным фолбэком:
  const tagline = t("footer_tagline", "Ваш гид по Коста дель Соль");
  const navTitle = t("footer_nav_title", "Навигация");
  const contactsTitle = t("contacts"); // ключ уже есть в твоём JSON
  const rights = t("footer_rights", "Все права защищены.");

  return (
    <footer className="footer">
      <div className="footer-container">
        {/* Левая часть: логотип и слоган */}
        <div className="footer-left">
          <h2 className="footer-logo">CostaSolinfo</h2>
          <p className="footer-slogan">{tagline}</p>
        </div>

        {/* Средняя часть: ссылки (SPA-навигация через <Link />) */}
        <div className="footer-links">
          <h4>{navTitle}</h4>
          <ul>
            <li><Link to="/">{t("home")}</Link></li>
            <li><Link to="/excursions">{t("excursions")}</Link></li>
            <li><Link to="/info-meeting">{t("info_meeting")}</Link></li>
            <li><Link to="/airport-transfer">{t("airport_transfer")}</Link></li>
            <li><Link to="/ask">{t("ask")}</Link></li> {/* добавили */}
            <li><Link to="/contacts">{t("contacts")}</Link></li>
            <li><Link to="/about">{t("about")}</Link></li>
          </ul>
        </div>

        {/* Правая часть: контакты + соцсети */}
        <div className="footer-right">
          <h4>{contactsTitle}</h4>
          <p>
            Email:{" "}
            <a href="mailto:CostaSolinfo.Malaga@gmail.com">
              CostaSolinfo.Malaga@gmail.com
            </a>
          </p>
          <p>
            WhatsApp:{" "}
            <a href="https://wa.me/34660535089" target="_blank" rel="noreferrer">
              +34 660 535 089
            </a>
          </p>

          <div className="footer-socials">
            <a href="https://facebook.com" target="_blank" rel="noreferrer" aria-label="Facebook">
              <i className="fab fa-facebook"></i>
            </a>
            <a href="https://instagram.com" target="_blank" rel="noreferrer" aria-label="Instagram">
              <i className="fab fa-instagram"></i>
            </a>
            <a href="https://wa.me/34660535089" target="_blank" rel="noreferrer" aria-label="WhatsApp">
              <i className="fab fa-whatsapp"></i>
            </a>
          </div>
        </div>
      </div>

      {/* Нижняя полоса */}
      <div className="footer-bottom">
        <p>© {year} CostaSolinfo. {rights}</p>
      </div>
    </footer>
  );
};

export default Footer;
