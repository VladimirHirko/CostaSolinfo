// src/components/PickupMap.js
import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
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

const PickupMap = ({ hotel, pickupPoint }) => {
  if (!pickupPoint && !hotel) {
    return <p style={{ textAlign: "center" }}>Нет данных для отображения карты</p>;
  }

  const center = pickupPoint
    ? [pickupPoint.lat, pickupPoint.lng]
    : [hotel.lat, hotel.lng];

  return (
    <MapContainer
      center={center}
      zoom={13}
      style={{ height: "400px", width: "100%", borderRadius: "10px", marginTop: "20px" }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
      />

      {hotel && (
        <Marker position={[hotel.lat, hotel.lng]}>
          <Popup>Ваш отель: {hotel.name}</Popup>
        </Marker>
      )}

      {pickupPoint && (
        <Marker position={[pickupPoint.lat, pickupPoint.lng]}>
          <Popup>Точка сбора: {pickupPoint.name}</Popup>
        </Marker>
      )}
    </MapContainer>
  );
};

export default PickupMap;
