// src/components/PickupMap.js
import React, { useEffect, useRef, useMemo } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Исправляем баг с иконками Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

// Плавный контроллер вида без двойной анимации
const SmoothView = ({ lat, lng, zoom = 15 }) => {
  const map = useMap();
  const didInitRef = useRef(false);

  useEffect(() => {
    if (lat == null || lng == null) return;

    const target = L.latLng(lat, lng);
    const current = map.getCenter();
    const dist = current.distanceTo(target); // м

    if (!didInitRef.current) {
      map.setView(target, zoom, { animate: false });
      didInitRef.current = true;
      return;
    }

    if (dist < 1 && map.getZoom() === zoom) return;

    map.stop();
    map.flyTo(target, zoom, { animate: true, duration: 0.6 });
  }, [lat, lng, zoom, map]);

  return null;
};

const PickupMap = ({ hotel, pickupPoint }) => {
  // Центр: приоритет — точка сбора
  const center = useMemo(() => {
    if (pickupPoint?.lat != null && pickupPoint?.lng != null) {
      return [Number(pickupPoint.lat), Number(pickupPoint.lng)];
    }
    if (hotel?.lat != null && hotel?.lng != null) {
      return [Number(hotel.lat), Number(hotel.lng)];
    }
    return null;
  }, [pickupPoint?.lat, pickupPoint?.lng, hotel?.lat, hotel?.lng]);

  if (!center) {
    return <p style={{ textAlign: "center" }}>Нет данных для отображения карты</p>;
  }

  return (
    <MapContainer
      center={center}
      zoom={15}
      // ✅ ВКЛЮЧАЕМ wheel-zoom, чтобы пинч на трекпаде работал
      scrollWheelZoom={true}
      // Для телефонов/планшетов оставляем пинч по touch
      touchZoom={true}
      dragging={true}
      tap={false}
      zoomControl={true}
      style={{
        height: "400px",
        width: "100%",
        borderRadius: "10px",
        marginTop: "20px",
        touchAction: "auto",
      }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
      />

      {hotel?.lat != null && hotel?.lng != null && (
        <Marker position={[Number(hotel.lat), Number(hotel.lng)]}>
          <Popup>Ваш отель: {hotel.name}</Popup>
        </Marker>
      )}

      {pickupPoint?.lat != null && pickupPoint?.lng != null && (
        <Marker position={[Number(pickupPoint.lat), Number(pickupPoint.lng)]}>
          <Popup>Точка сбора: {pickupPoint.name}</Popup>
        </Marker>
      )}

      <SmoothView
        lat={pickupPoint?.lat ?? hotel?.lat}
        lng={pickupPoint?.lng ?? hotel?.lng}
        zoom={15}
      />
    </MapContainer>
  );
};

export default PickupMap;
