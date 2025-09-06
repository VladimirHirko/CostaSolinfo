// helpers/normalizeText.js
export const normalizeText = (val) => {
  if (val == null) return '';
  let s = String(val);

  // нормализация юникода
  s = s.normalize('NFKC');

  // заменить HTML-сущности
  s = s.replace(/&nbsp;/gi, ' ');

  // заменить неразрывные пробелы напрямую
  s = s.replace(/\u00A0/g, ' ');

  // убрать невидимые спецсимволы
  s = s.replace(/[\u200B\u200C\u200D\uFEFF]/g, '');

  // убрать пробелы в начале/конце
  s = s.replace(/^\s+|\s+$/g, '');

  // заменить множественные пробелы на один
  s = s.replace(/\s+/g, ' ');

  return s;
};
