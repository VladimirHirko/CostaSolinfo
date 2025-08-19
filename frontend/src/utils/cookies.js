// frontend/src/utils/cookies.js
export const CONSENT_COOKIE = 'csi_consent';
const MAX_AGE = 60 * 60 * 24 * 180; // 180 дней

export function readCookie(name) {
  const m = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return m ? decodeURIComponent(m[1]) : null;
}

export function writeCookie(name, value, { maxAge = MAX_AGE, path = '/', sameSite = 'Lax', secure } = {}) {
  const parts = [
    `${name}=${encodeURIComponent(value)}`,
    `Max-Age=${maxAge}`,
    `Path=${path}`,
    `SameSite=${sameSite}`,
  ];
  const isHttps = typeof window !== 'undefined' && window.location && window.location.protocol === 'https:';
  const useSecure = secure ?? isHttps;
  if (useSecure) parts.push('Secure');
  document.cookie = parts.join('; ');
}

export function getConsent() {
  const raw = readCookie(CONSENT_COOKIE);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { return null; }
}

/**
 * consent: { essential: true, analytics: boolean, marketing: boolean, preferences?: boolean, ts: number }
 */
export function setConsent(consentObj) {
  const payload = JSON.stringify(consentObj);
  writeCookie(CONSENT_COOKIE, payload);
  // Событие для подписчиков (например, модуль аналитики)
  window.dispatchEvent(new Event('csi-consent-updated'));
}

export function hasConsent(category) {
  const c = getConsent();
  return !!(c && c[category] === true);
}
