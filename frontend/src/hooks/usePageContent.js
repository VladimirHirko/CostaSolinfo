import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

export const usePageContent = (endpoint) => {
  const [data, setData] = useState(null);
  const { i18n } = useTranslation();

  useEffect(() => {
    fetch(`/api/${endpoint}/`, {
      headers: { 'Accept-Language': i18n.language }
    })
      .then(res => res.json())
      .then(json => setData(json))
      .catch(err => console.error(err));
  }, [endpoint, i18n.language]);

  return data;
};
