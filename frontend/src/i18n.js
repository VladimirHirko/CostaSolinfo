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
  en: { translation: translationEN },
  ru: { translation: translationRU },
  lt: { translation: translationLT },
  lv: { translation: translationLV },
  et: { translation: translationET },
  uk: { translation: translationUK },
  es: { translation: translationES },
};

const SUPPORTED = ['en', 'ru', 'lt', 'lv', 'et', 'uk', 'es'];

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',                 // если языка нет — откатываемся на EN
    supportedLngs: SUPPORTED,          // допустимые короткие коды
    load: 'languageOnly',              // 'lt-LT' -> 'lt'
    nonExplicitSupportedLngs: true,    // принимать 'xx-YY' как 'xx'
    detection: {
      // приоритет: ?lang=xx -> localStorage -> язык браузера -> атрибут <html lang="">
      order: ['querystring', 'localStorage', 'navigator', 'htmlTag'],
      lookupQuerystring: 'lang',
      caches: ['localStorage'],
    },
    interpolation: { escapeValue: false },
    returnEmptyString: false,
  });

// обновляем <html lang="..."> при смене языка
i18n.on('languageChanged', (lng) => {
  document.documentElement.lang = (lng || 'en');
});

export default i18n;
