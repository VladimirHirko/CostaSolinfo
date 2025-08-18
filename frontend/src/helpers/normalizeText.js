// helpers/normalizeText.js (один раз)
export const normalizeText = (val) => {
  if (val == null) return '';
  let s = String(val);
  s = s.normalize('NFKC');
  s = s.replace(/\u00A0/g, ' ');
  s = s.replace(/[\u200B\u200C\u200D\uFEFF]/g, '');
  s = s.replace(/^\s+|\s+$/g, '');
  s = s.replace(/\s+/g, ' ');
  return s;
};
