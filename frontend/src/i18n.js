// src/i18n.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import translationRU from './locales/ru/translation.json';
import translationEN from './locales/en/translation.json';
import translationLT from './locales/lt/translation.json';
import translationLV from './locales/lv/translation.json';
import translationET from './locales/et/translation.json';
import translationUK from './locales/uk/translation.json';
import translationES from './locales/es/translation.json';

const resources = {
  ru: { translation: translationRU },
  en: { translation: translationEN },
  lt: { translation: translationLT },
  lv: { translation: translationLV },
  et: { translation: translationET },
  uk: { translation: translationUK },
  es: { translation: translationES },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'ru', // язык по умолчанию
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
