import React from 'react';
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';

const containerStyle = {
  width: '100%',
  height: '400px'
};

const center = {
  lat: 36.5962, // заменишь на свои координаты
  lng: -4.5522
};

function MapComponent({ lat, lng }) {
  const center = { lat: parseFloat(lat), lng: parseFloat(lng) };
  
  return (
    <LoadScript googleMapsApiKey="AIzaSyBeOBhSGnhR7IXFLUp-ODD62mNuzokODDA">
      <GoogleMap
        mapContainerStyle={containerStyle}
        center={center}
        zoom={10}
      >
        <Marker position={center} />
      </GoogleMap>
    </LoadScript>
  );
}

export default MapComponent;
