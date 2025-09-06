export async function fetchExcursionRules(lang) {
  const res = await fetch(`/api/excursions/rules/?lang=${lang}`);
  if (!res.ok) throw new Error("Failed to load rules");
  return res.json(); // { language_code, title, content }
}
