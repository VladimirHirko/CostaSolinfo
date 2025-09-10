// frontend/src/api/excursions.js
export async function fetchExcursionLongDetail(id, lang = 'en') {
  const res = await fetch(`/api/excursions/${id}/long-detail/?lang=${lang}`);
  if (!res.ok) throw new Error('Failed to load long detail');
  return res.json();
}
