import React, { useState, useEffect } from 'react'; // <<< FIX: Added useEffect import
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import RoomPage from './pages/RoomPage';
import { ApiService } from './api/ApiService';

// --- Home Component to Create/Join Room ---
const Home: React.FC = () => {
 const [inputRoomId, setInputRoomId] = useState('');
 const navigate = useNavigate();

 const handleCreateRoom = async () => {
  try {
   // Calls POST /api/v1/rooms
   const roomId = await ApiService.createRoom();
   navigate(`/room/${roomId}`);
  } catch (e) {
   alert('Failed to create room. Is the backend running?');
  }
 };

 const handleJoinRoom = () => {
  if (inputRoomId) {
   navigate(`/room/${inputRoomId}`);
  }
 };

 return (
  <div style={{ padding: '40px', maxWidth: '400px', margin: 'auto' }}>
   <h1>Pair Programming App</h1>
   
   {/* Create Room */}
   <button onClick={handleCreateRoom} style={{ marginBottom: '20px', padding: '10px 20px' }}>
    🚀 Create New Room
   </button>

   <h2>— OR —</h2>

   {/* Join Room */}
   <input
    type="text"
    placeholder="Enter Room ID"
    value={inputRoomId}
    onChange={(e) => setInputRoomId(e.target.value)}
    style={{ width: '100%', padding: '10px', margin: '10px 0' }}
   />
   <button onClick={handleJoinRoom} disabled={!inputRoomId} style={{ padding: '10px 20px', width: '100%' }}>
    Join Existing Room
   </button>
   
   <HealthCheckDisplay />
  </div>
 );
};

// --- Simple Health Check Display ---
const HealthCheckDisplay: React.FC = () => {
  const [isHealthy, setIsHealthy] = useState(false);

  useEffect(() => { // <<< This hook requires the import
    // Check health status on load (calls GET /api/v1/health)
    ApiService.checkHealth().then(setIsHealthy);
    
    // Polling (optional)
    const interval = setInterval(() => {
      ApiService.checkHealth().then(setIsHealthy);
    }, 10000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <p style={{ marginTop: '30px', fontSize: '14px' }}>
      Backend Status: 
      <span style={{ color: isHealthy ? 'green' : 'red', fontWeight: 'bold' }}>
        {isHealthy ? ' ONLINE & DB CONNECTED' : ' OFFLINE or DB ERROR'}
      </span>
    </p>
  );
}

// --- Main Application Component ---
const App: React.FC = () => {
 return (
  <Router>
   <Routes>
    <Route path="/" element={<Home />} />
    {/* Route for joining a room */}
    <Route path="/room/:roomId" element={<RoomPage />} /> 
   </Routes>
  </Router>
 );
};

export default App;