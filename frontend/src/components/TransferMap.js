// TransferMap.js
import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Настройка иконки маркера
const customIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

// Компонент перелёта карты к новой точке
const FlyToLocation = ({ lat, lng }) => {
  const map = useMap();

  useEffect(() => {
    if (lat && lng) {
      map.flyTo([lat, lng], 18, {
        duration: 1.5,
      });
    }
  }, [lat, lng]);

  return null;
};

const TransferMap = ({ lat, lng, pickupName }) => {
  if (!lat || !lng) return null;

  return (
    <div style={{ height: '400px', marginTop: '30px', borderRadius: '12px', overflow: 'hidden' }}>
      <MapContainer center={[lat, lng]} zoom={13} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
        />
        <Marker position={[lat, lng]} icon={customIcon}>
          <Popup>{pickupName || 'Точка сбора'}</Popup>
        </Marker>
        {/* Плавный перелет к новой точке */}
        <FlyToLocation lat={lat} lng={lng} />
      </MapContainer>
    </div>
  );
};

export default TransferMap;
