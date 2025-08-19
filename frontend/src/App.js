// src/App.js
import React, { useEffect, useState } from 'react';     // ⬅️ добавили useEffect, useState
import './styles/main.css';
import './styles/navbar.css';
import 'leaflet/dist/leaflet.css';

import ExcursionsPage from "./pages/ExcursionsPage";
import ExcursionDetailPage from "./pages/ExcursionDetailPage";

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import HomePage from './pages/HomePage';
import InfoMeetingPage from './pages/InfoMeetingPage';
import AirportTransferChoicePage from './pages/AirportTransferChoicePage';
import AirportTransferGroupPage from './pages/AirportTransferGroupPage';
import AirportTransferPrivatePage from './pages/AirportTransferPrivatePage';
import AskQuestionPage from './pages/AskQuestionPage';
import ContactsPage from './pages/ContactsPage';
import AboutUsPage from './pages/AboutUsPage';

import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ScrollToTopButton from './components/ScrollToTopButton';
import CookieBanner from './components/CookieBanner';
import PrivacyPolicyModal from './components/PrivacyPolicyModal';  // ⬅️ НОВОЕ

function App() {
  const [openPrivacy, setOpenPrivacy] = useState(false); // ⬅️ НОВОЕ

  // Глобальная функция, чтобы открыть модалку откуда угодно (баннер/футер)
  useEffect(() => {
    window.csiOpenPrivacy = () => setOpenPrivacy(true);
    return () => { delete window.csiOpenPrivacy; };
  }, []);

  return (
    <Router>
      <Navbar />

      <div className="main-container" style={{ padding: '20px' }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/excursions" element={<ExcursionsPage />} />
          <Route path="/excursion/:id" element={<ExcursionDetailPage />} />
          <Route path="/info-meeting" element={<InfoMeetingPage />} />
          <Route path="/airport-transfer" element={<AirportTransferChoicePage />} />
          <Route path="/airport-transfer/group" element={<AirportTransferGroupPage />} />
          <Route path="/airport-transfer/private" element={<AirportTransferPrivatePage />} />
          <Route path="/ask" element={<AskQuestionPage />} />
          <Route path="/contacts" element={<ContactsPage />} />
          <Route path="/about" element={<AboutUsPage />} />
        </Routes>
      </div>

      <CookieBanner />
      <Footer />
      <ScrollToTopButton />

      {/* ⬇️ Модалка политики — монтируется один раз на всём приложении */}
      <PrivacyPolicyModal
        isOpen={openPrivacy}
        onClose={() => setOpenPrivacy(false)}
      />
    </Router>
  );
}

export default App;
