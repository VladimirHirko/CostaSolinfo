import React, { useEffect } from "react";
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

// 🔹 Компонент для плавного перелёта карты
const FlyToLocation = ({ lat, lng }) => {
  const map = useMap();

  useEffect(() => {
    if (lat && lng) {
      map.flyTo([lat, lng], 15, {
        duration: 1.5,
      });
    }
  }, [lat, lng, map]);

  return null;
};

const PickupMap = ({ hotel, pickupPoint }) => {
  if (
    (!pickupPoint || pickupPoint.lat == null || pickupPoint.lng == null) &&
    (!hotel || hotel.lat == null || hotel.lng == null)
  ) {
    return <p style={{ textAlign: "center" }}>Нет данных для отображения карты</p>;
  }

  const center =
    pickupPoint?.lat && pickupPoint?.lng
      ? [pickupPoint.lat, pickupPoint.lng]
      : [hotel.lat, hotel.lng];

  return (
    <MapContainer
      center={center}
      zoom={15}
      style={{
        height: "400px",
        width: "100%",
        borderRadius: "10px",
        marginTop: "20px",
      }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
      />

      {hotel?.lat && hotel?.lng && (
        <Marker position={[hotel.lat, hotel.lng]}>
          <Popup>Ваш отель: {hotel.name}</Popup>
        </Marker>
      )}

      {pickupPoint?.lat && pickupPoint?.lng && (
        <Marker position={[pickupPoint.lat, pickupPoint.lng]}>
          <Popup>Точка сбора: {pickupPoint.name}</Popup>
        </Marker>
      )}

      {/* 🔹 Плавный перелёт */}
      <FlyToLocation lat={pickupPoint?.lat || hotel?.lat} lng={pickupPoint?.lng || hotel?.lng} />
    </MapContainer>
  );
};

export default PickupMap;
