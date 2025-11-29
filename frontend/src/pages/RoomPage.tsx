import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ApiService } from '../api/ApiService';
// Assuming you have a CodeEditor component
// import CodeEditor from '../components/CodeEditor'; 

const language = 'python'; // Hardcoded language for the backend mock

interface RoomParams {
  roomId: string;
}

const RoomPage: React.FC = () => {
  const { roomId } = useParams<keyof RoomParams>() as RoomParams;
  const navigate = useNavigate();
  
  const wsRef = useRef<WebSocket | null>(null);
  const [code, setCode] = useState<string>('');
  const [suggestion, setSuggestion] = useState<string>('');
  const [status, setStatus] = useState<'connecting' | 'connected' | 'error' | 'loading'>('loading');

  // --- 1. WebSocket Connection Logic ---
  useEffect(() => {
    if (!roomId) {
      setStatus('error');
      return;
    }
    
    setStatus('connecting');
    try {
      const ws = ApiService.connectWebSocket(roomId);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus('connected');
        console.log(`WebSocket connected to room: ${roomId}`);
      };

      ws.onmessage = (event) => {
        // Received new code from a peer or initial state from server
        setCode(event.data);
      };

      ws.onclose = () => {
        setStatus('error');
        console.log('WebSocket disconnected.');
      };

      ws.onerror = (error) => {
        console.error('WebSocket Error:', error);
        setStatus('error');
      };

    } catch (e) {
      console.error('Failed to initiate WebSocket:', e);
      setStatus('error');
    }

    // Cleanup on unmount or roomId change
    return () => {
      wsRef.current?.close();
    };
  }, [roomId]);

  // --- 2. Code Change Handler (Sends Update and Triggers Autocomplete) ---
  const handleCodeChange = (newCode: string, cursorPosition: number) => {
    setCode(newCode);

    // a) Broadcast to peers (send full content)
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(newCode);
    }

    // b) Trigger mock autocomplete (simplified debounce logic)
    getSuggestion(newCode, cursorPosition);
  };
  
  // Simplified debounce ref
  const autocompleteTimer = useRef<NodeJS.Timeout | null>(null);

  const getSuggestion = useCallback((code: string, cursorPosition: number) => {
    if (autocompleteTimer.current) {
      clearTimeout(autocompleteTimer.current);
    }
    
    autocompleteTimer.current = setTimeout(async () => {
      try {
        const payload = { code, cursorPosition, language };
        const result = await ApiService.getAutocomplete(payload);
        setSuggestion(result.suggestion);
      } catch (e) {
        setSuggestion('AI service unavailable.');
      }
    }, 600); // 600ms debounce delay
  }, []);

  // --- 3. UI Rendering ---
  return (
    <div style={{ padding: '20px' }}>
      <h1>Pair Programming Room: {roomId}</h1>
      <p>Status: <span style={{ color: status === 'connected' ? 'green' : 'red' }}>{status.toUpperCase()}</span></p>

      {status === 'error' && (
        <p>Could not connect to the room. Please check the room ID and server status.</p>
      )}

      {/* Placeholder for the Code Editor component */}
      <div 
        style={{ border: '1px solid #ccc', minHeight: '300px', whiteSpace: 'pre-wrap' }}
        // In a real app, this would be an editor like Monaco or Ace
      >
        <textarea
          value={code}
          onChange={(e) => handleCodeChange(e.target.value, e.target.selectionStart)}
          style={{ width: '100%', height: '300px', fontFamily: 'monospace' }}
        />
      </div>

      <h2>Autocomplete Suggestion:</h2>
      <pre style={{ backgroundColor: '#eee', padding: '10px' }}>{suggestion}</pre>
      
      <button onClick={() => navigate('/')}>Go Home</button>
    </div>
  );
};

export default RoomPage;