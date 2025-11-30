# 📚 Real-Time Pair Programming (Full-Stack Application)

This project is a full-stack, collaborative, real-time code editor designed for pair programming. It features a **React** frontend and a **FastAPI** backend, enabling multiple users to code together seamlessly in a shared room.

## 🌟 Features

### Frontend (React)
  * **Collaborative Editor:** Integrates the **Monaco Editor** (the engine behind VS Code) for a professional coding experience.
  * **Real-Time Sync:** Uses WebSockets to receive and broadcast code changes instantly to all participants in a room.
  * **Syntax Highlighting:** Automatic language detection and syntax highlighting provided by Monaco.
  * **Room Management:** Simple UI to create or join programming rooms.

### Backend (FastAPI)
  * **High-Performance API:** Built with **FastAPI** for fast, asynchronous request handling.
  * **WebSocket Communication:** A dedicated WebSocket endpoint (`/api/v1/ws/{room_id}`) manages real-time communication for low-latency code synchronization.
  * **Persistent State:** Leverages **PostgreSQL** and **SQLAlchemy** to save room state and code, ensuring work is not lost between sessions.
  * **Scalable Structure:** Follows a clean, scalable repository structure (routers, CRUD, models, schemas).
  * **Health & Liveness Probes:** Includes `/health` and `/liveness` endpoints for robust monitoring and container orchestration.
  * **Robust Logging:** Centralized logger with detailed output (file path, line number) for easy debugging.

## 🚀 Getting Started

### Prerequisites

  * **Docker** and **Docker Compose** (Recommended method for running the database and application).
  * **Node.js & npm** (if running the frontend locally).
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
                "password": "*****",
                "database": "collab_db"
            }
        }
    }
    ```

    *Note: The `host` is set to `db` to correctly reference the Postgres container within the Docker network.*

2.  **Backend Dependencies:** Ensure you have a `requirements.txt` listing packages like `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2-binary`, and `pydantic-settings`.

3.  **Frontend Dependencies:** The `frontend/` directory should contain a `package.json` file.

### Running with Docker Compose (Recommended)

This is the fastest way to run the entire full-stack application (Frontend, Backend, and Database).

1.  Ensure you have a `Dockerfile` for the backend (in `backend/`) and a `Dockerfile` for the frontend (in `frontend/`).

2.  Run the following command from the project root:

    ```bash
    docker-compose up --build
    ```
    
    This will:
    - Build the frontend and backend images.
    - Start containers for the frontend, backend, and PostgreSQL database.

The frontend will be accessible at `http://localhost:3000`, and the backend API will be available at `http://localhost:8000`.

-----

## Development Setup

Before running the application or tests, set up the environment and install the required dependencies.

1.  **Create and activate a virtual environment:**

    ```shell
    # Create the virtual environment
    py -m venv .venv

    # Activate it (on Windows)
    .\.venv\Scripts\activate
    ```

2.  **Install dependencies:**
    Install all the necessary packages using the `requirements.txt` file.

    ```shell
    # Ensure pip is up-to-date
    py -m pip install --upgrade pip

    # Install project dependencies
    py -m pip install -r requirements.txt
    ```
    *(If you don't have a `requirements.txt` file, you can create one with `py -m pip freeze > requirements.txt` after installing your packages.)*


## Running Tests

To run the test suite, execute the following command from the root of the project. The `-vv` flag provides detailed (very verbose) output.

```shell
py -m pytest .\backend\test\ -vv
```


## 🛠️ API Endpoints

For convenience, a collection of sample requests is available in `backend/curl.yaml`. This file can be imported directly into API clients like Insomnia to test the endpoints.

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

The project is structured as a monorepo with distinct `frontend` and `backend` directories, promoting separation of concerns.

### Backend Architecture

The backend follows the standard "FastAPI Project Template" pattern for maximum scalability and maintainability:
  * **`app/core`**: Configuration (`config.py`), logging (`logger.py`), and WebSocket management (`ws_manager.py`).
  * **`app/api/v1/endpoints`**: Contains route logic (`coding.py`) for REST and WebSockets.
  * **`app/crud`**: Data access layer, isolating SQLAlchemy logic.
  * **`app/models`**: SQLAlchemy models (defines the `Room` table).
  * **`app/schemas`**: Pydantic models (data validation and serialization).

### Frontend Architecture
  * **`src/components`**: Reusable React components, including the main `Editor` component that wraps Monaco.
  * **`src/pages`**: Top-level components for different views, like the `HomePage` and `EditorPage`.
  * **`src/hooks`**: Custom hooks to manage complex logic, such as the `useWebSocket` hook for handling real-time communication.
  * **State Management**: Utilizes React's Context API or a library like Zustand for managing global state, such as the current room ID and user information.

### Backend Design Choices

#### Configuration (`config.json` & Pydantic)
Configuration uses a layered approach for security and flexibility:

1.  **Pydantic Settings:** `BaseSettings` handles loading, but the fields are required.
2.  **`@model_validator`:** A `model_validator(mode='before')` is used to load database credentials from the external `config.json` **before** Pydantic performs validation, solving the common Pydantic v2 "Field required" error with file-based config.
3.  **Environment Isolation:** The configuration is nested under the `"PRODUCTION"` key, allowing easy expansion for `DEVELOPMENT` or `STAGING` environments.

#### WebSocket Handling

  * **Connection Manager (`ws_manager.py`):** This singleton class holds a dictionary (`active_connections`) mapping `room_id` to a list of active `WebSockets`, efficiently handling broadcasting and disconnection tracking.
  * **Initial State:** Upon connecting, the server checks the database for the room's persistent code and sends it to the client, ensuring the client is always synced upon joining.
  * **CORS Fix:** Explicit origins were added to the `CORSMiddleware` in `main.py` to resolve the common **403 Forbidden** error specific to WebSocket handshake requests in development environments like Insomnia and `wscat`.

-----

## 🔮 Future Improvements

1.  **Optimistic UI/Operation Transformation (OT):** The current implementation uses a "last-write wins" sync model, sending the entire code state on every change. For a production app, this would be replaced with **Operation Transformation (OT)** or **CRDTs (Conflict-free Replicated Data Types)** to send only diffs, reducing bandwidth and eliminating collaboration conflicts.
2.  **Asynchronous CRUD:** Switch database operations in the CRUD layer to use `asyncpg` or `asyncio` with SQLAlchemy 2.0+ to fully utilize FastAPI's asynchronous nature.
3.  **Authentication:** Implement proper JWT or OAuth authentication, replacing the simple `x-username` header with a security dependency.
4.  **In-Memory Caching:** Use Redis to cache the code content, reducing the load on the PostgreSQL database for every code update.