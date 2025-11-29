import { AutocompleteRequest, AutocompleteResponse } from '../types/ApiTypes';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// --- Global User Information (Simulated Auth Headers) ---
const USER_HEADERS = {
  'x-username': 'rahul',
  'x-usermail': 'rahul_pair_programming@gmail.com',
};
// -------------------------------------------------------

export class ApiService {
  /**
   * REST: Creates a new room and returns its ID.
   */
  public static async createRoom(): Promise<string> {
    const url = `${API_BASE_URL}/rooms`;
    
    // Include custom headers for tracking
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...USER_HEADERS,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to create room: ${response.statusText}`);
    }

    const data = await response.json();
    return data.roomId;
  }

  /**
   * REST: Gets a mocked autocomplete suggestion.
   */
  public static async getAutocomplete(
    payload: AutocompleteRequest
  ): Promise<AutocompleteResponse> {
    const url = `${API_BASE_URL}/autocomplete`;
    
    // Include custom headers for tracking
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...USER_HEADERS,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Autocomplete failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * REST: Performs a health check (includes DB connection).
   */
  public static async checkHealth(): Promise<boolean> {
    const url = `${API_BASE_URL}/health`;
    try {
      const response = await fetch(url, { method: 'GET' });
      return response.ok;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  /**
   * WebSocket: Establishes the real-time connection.
   * NOTE: WebSockets do not send headers directly in the connection frame.
   * The server relies on the CORS handshake and the URL path.
   */
  public static connectWebSocket(roomId: string): WebSocket {
    // Corrected path to include /api/v1/ws/
    const wsUrl = `ws://localhost:8000/api/v1/ws/${roomId}`;
    
    // Ensure the client sends the Origin header for CORS
    // In React/Browser environments, this is usually handled implicitly, 
    // but the backend is now explicitly configured to accept the WebSocket upgrade request.
    const ws = new WebSocket(wsUrl);
    
    // Since we can't set custom headers directly on a native WebSocket 
    // object, we rely on the CORS middleware accepting the connection.
    return ws;
  }
}

// Placeholder types for clarity
export interface AutocompleteRequest {
  code: string;
  cursorPosition: number;
  language: string;
}

export interface AutocompleteResponse {
  suggestion: string;
}