import http from "../api/http";
import i18n from '../i18n';

const http = axios.create({ /* baseURL если есть */ });

http.interceptors.request.use((config) => {
  const lng = (i18n.resolvedLanguage || 'en').split('-')[0];
  config.headers['Accept-Language'] = lng;
  return config;
});

export default http;
