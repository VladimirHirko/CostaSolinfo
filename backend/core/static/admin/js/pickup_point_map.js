document.addEventListener('DOMContentLoaded', function () {
  const latInput = document.querySelector('#id_latitude');
  const lngInput = document.querySelector('#id_longitude');

  if (!latInput || !lngInput) return;

  const mapDiv = document.createElement('div');
  mapDiv.id = 'pickup-map';
  mapDiv.style = 'height: 400px; margin-top: 15px; border: 1px solid #ccc;';
  lngInput.parentElement.appendChild(mapDiv);

  const map = L.map('pickup-map').setView([36.6, -4.5], 10); // центр Коста-дель-Соль

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  let marker = null;

  function updateMarker(lat, lng) {
    if (marker) map.removeLayer(marker);
    marker = L.marker([lat, lng]).addTo(map);
  }

  map.on('click', function (e) {
    const lat = e.latlng.lat.toFixed(6);
    const lng = e.latlng.lng.toFixed(6);
    latInput.value = lat;
    lngInput.value = lng;
    updateMarker(lat, lng);
  });

  // если координаты уже введены — показать маркер
  if (latInput.value && lngInput.value) {
    updateMarker(latInput.value, lngInput.value);
    map.setView([latInput.value, lngInput.value], 12);
  }
});
