# 📚 Real-Time Pair Programming Backend (FastAPI)

This project implements the backend for a collaborative, real-time code editor and pair-programming application. It uses **FastAPI** for high-performance API endpoints and **WebSockets** for instant code synchronization between users.

## 🌟 Features

  * **Standardized Structure:** Clean, scalable repository structure based on the FastAPI Project Template (routers, CRUD, core, models, schemas).
  * **Real-Time Sync:** WebSocket endpoint (`/api/v1/ws/{room_id}`) for low-latency code broadcasting.
  * **Persistent State:** Uses **PostgreSQL** (via Docker Compose) and **SQLAlchemy** to maintain room state and code content.
  * **Health Monitoring:** Dedicated Liveness (`/liveness`) and Health Check (`/health`) endpoints.
  * **Mock AI:** Mocked Autocomplete endpoint for simulating AI suggestions.
  * **Robust Logging:** Single, globally initialized logger (`app/core/logger.py`) used across the application, including file path and line number for easy debugging.
  * **Custom Headers:** Tracks user identity (`x-username`, `x-usermail`) via request headers.

## 🚀 Getting Started

### Prerequisites

  * **Docker** and **Docker Compose** (Recommended method for running the database and application).
  * Python 3.12+ (if running locally without Docker).

### Project Setup

1.  **Configuration:** Create the `config.json` file in the root directory (where `docker-compose.yml` is located) to define the database connection details:

    **`config.json`**

    ```json
    {
        "PRODUCTION": {
            "db_config": {
                "host": "db",
                "port": 5432,
                "user": "postgres",
                "password": "Rv@123",
                "database": "collab_db"
            }
        }
    }
    ```

    *Note: The `host` is set to `db` to correctly reference the Postgres container within the Docker network.*

2.  **Dependencies:** Ensure you have a `requirements.txt` listing packages like `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2-binary`, and `pydantic-settings`.

### Running with Docker Compose (Recommended)

This is the fastest way to run both the FastAPI application and the required PostgreSQL database.

1.  Place the `Dockerfile` inside the `backend/` folder.

2.  Run the following command from the project root:

    ```bash
    docker-compose up --build
    ```

The application will be accessible at `http://localhost:8000`.

-----

## 🛠️ API Endpoints

All REST endpoints use the prefix `/api/v1`. The following cURL commands demonstrate access using the required custom headers (`x-username: rahul`, `x-usermail: rahul_pair_programming@gmail.com`).

### 1\. Create a New Room

**`POST /api/v1/rooms`**

| Header | Value |
| :--- | :--- |
| `x-username` | `rahul` |
| `x-usermail` | `rahul_pair_programming@gmail.com` |

```bash
curl -X POST 'http://localhost:8000/api/v1/rooms' \
-H 'accept: application/json' \
-H 'x-username: rahul' \
-H 'x-usermail: rahul_pair_programming@gmail.com'
```

### 2\. Mock Autocomplete

**`POST /api/v1/autocomplete`**

| Header | Value |
| :--- | :--- |
| `Content-Type` | `application/json` |

```bash
curl -X POST 'http://localhost:8000/api/v1/autocomplete' \
-H 'Content-Type: application/json' \
-d '{
  "code": "def my_func",
  "cursorPosition": 12,
  "language": "python"
}'
```

### 3\. Health Checks

| Endpoint | Purpose | Success Status |
| :--- | :--- | :--- |
| **GET /api/v1/liveness** | Checks if the process is running. | `200 OK` |
| **GET /api/v1/health** | Checks if the process AND database are accessible. | `200 OK` (or `503 Service Unavailable` if DB is down) |

```bash
# Liveness Check
curl 'http://localhost:8000/api/v1/liveness'

# Health Check (DB connection check)
curl 'http://localhost:8000/api/v1/health'
```

### 4\. WebSocket Connection (Real-Time)

**`WS /api/v1/ws/{room_id}`**

Use a WebSocket client (like Insomnia or `wscat`) to connect. The custom `Origin` header is required to pass the CORS handshake.

```bash
# Example using wscat (replace {room_id} with a valid ID)
wscat -c ws://localhost:8000/api/v1/ws/{room_id} -H "Origin: http://localhost:3000"
```

-----

## 🏗️ Architecture and Design Choices

### Project Structure

The project follows the standard "FastAPI Project Template" pattern for maximum scalability and maintainability:

  * **`app/core`**: Configuration (`config.py`), logging (`logger.py`), and WebSocket management (`ws_manager.py`).
  * **`app/api/v1/endpoints`**: Contains route logic (`coding.py`) for REST and WebSockets.
  * **`app/crud`**: Data access layer, isolating SQLAlchemy logic.
  * **`app/models`**: SQLAlchemy models (defines the `Room` table).
  * **`app/schemas`**: Pydantic models (data validation and serialization).

### Configuration (`config.json` & Pydantic)

Configuration uses a layered approach:

1.  **Pydantic Settings:** `BaseSettings` handles loading, but the fields are required.
2.  **`@model_validator`:** A `model_validator(mode='before')` is used to load database credentials from the external `config.json` **before** Pydantic performs validation, solving the common Pydantic v2 "Field required" error with file-based config.
3.  **Environment Isolation:** The configuration is nested under the `"PRODUCTION"` key, allowing easy expansion for `DEVELOPMENT` or `STAGING` environments.

### WebSocket Handling

  * **Connection Manager (`ws_manager.py`):** This singleton class holds a dictionary (`active_connections`) mapping `room_id` to a list of active `WebSockets`, efficiently handling broadcasting and disconnection tracking.
  * **Initial State:** Upon connecting, the server checks the database for the room's persistent code and sends it to the client, ensuring the client is always synced upon joining.
  * **CORS Fix:** Explicit origins were added to the `CORSMiddleware` in `main.py` to resolve the common **403 Forbidden** error specific to WebSocket handshake requests in development environments like Insomnia and `wscat`.

-----

## 🔮 Future Improvements

1.  **Optimistic UI/Operation Transformation (OT):** The current implementation uses a "last-write wins" sync model, sending the entire code state on every change. For a production app, this would be replaced with **Operation Transformation (OT)** or **CRDTs (Conflict-free Replicated Data Types)** to send only diffs, reducing bandwidth and eliminating collaboration conflicts.
2.  **Asynchronous CRUD:** Switch database operations in the CRUD layer to use `asyncpg` or `asyncio` with SQLAlchemy 2.0+ to fully utilize FastAPI's asynchronous nature.
3.  **Authentication:** Implement proper JWT or OAuth authentication, replacing the simple `x-username` header with a security dependency.
4.  **In-Memory Caching:** Use Redis to cache the code content, reducing the load on the PostgreSQL database for every code update.