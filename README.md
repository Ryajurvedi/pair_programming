# Real-Time Pair Programming Prototype

A simplified real-time collaboration tool allowing users to join rooms and edit Python code simultaneously.

## Features
* **Room Management**: Create and join unique rooms via ID.
* **Real-time Collaboration**: WebSocket-based syncing ensures all users see updates instantly.
* **AI Autocomplete**: A mocked endpoint provides suggestions after a 600ms typing pause.

## [cite_start]Architecture [cite: 30]
* **Backend**: Python (FastAPI). Uses `ConnectionManager` to handle WebSocket broadcasting. Database abstraction allows for Postgres, though currently defaults to SQLite for ease of testing.
* **Frontend**: React. Manages WebSocket state and debounces API calls for the autocomplete feature.

## [cite_start]How to Run [cite: 29]

### Backend
1. Navigate to `/backend`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the server: `uvicorn main:app --reload`.
4. The API runs at `http://localhost:8000`.

### Frontend
1. Navigate to `/frontend`.
2. Install dependencies: `npm install`.
3. Start the client: `npm start`.
4. Open `http://localhost:3000`.

## [cite_start]Design Choices & Limitations [cite: 30, 32]
* **Sync Strategy**: Uses a "Last-Write-Wins" approach via broadcasting. In a production environment with high latency, Operational Transformation (OT) or CRDTs would be preferred to prevent overwrite conflicts.
* **Database**: Room state is persisted on every keystroke for simplicity. Production would require buffering/debouncing writes to Postgres to reduce load.

## [cite_start]Future Improvements [cite: 31]
* Implement Operational Transformation (OT) for better conflict resolution.
* Add syntax highlighting (e.g., Monaco Editor).
* Add Authentication for user identity.