// frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';

// Ensure this path points correctly to your App.tsx file

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);