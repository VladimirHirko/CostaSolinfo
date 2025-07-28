document.addEventListener("DOMContentLoaded", function () {
  const inlines = document.querySelectorAll(".dynamic-excursionpickuppoint_set");

  inlines.forEach((inline, index) => {
    const latInput = inline.querySelector("input[name$='latitude']");
    const lngInput = inline.querySelector("input[name$='longitude']");

    if (latInput && lngInput) {
      // контейнер карты
      const mapContainer = document.createElement("div");
      mapContainer.style = "width: 100%; height: 300px; margin: 1em 0;";
      inline.appendChild(mapContainer);

      const initialLat = parseFloat(latInput.value) || 36.6;
      const initialLng = parseFloat(lngInput.value) || -4.5;

      const map = L.map(mapContainer).setView([initialLat, initialLng], 12);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '© OpenStreetMap contributors'
      }).addTo(map);

      const marker = L.marker([initialLat, initialLng], { draggable: true }).addTo(map);

      // обновление по перетаскиванию
      marker.on("dragend", function () {
        const { lat, lng } = marker.getLatLng();
        latInput.value = lat.toFixed(6);
        lngInput.value = lng.toFixed(6);
      });

      // обновление по клику
      map.on("click", function (e) {
        marker.setLatLng(e.latlng);
        latInput.value = e.latlng.lat.toFixed(6);
        lngInput.value = e.latlng.lng.toFixed(6);
      });
    }
  });
});
