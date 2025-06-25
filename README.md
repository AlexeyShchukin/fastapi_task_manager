# FastAPI Task Manager 


FastAPI Task Manager is a simple task management API built using FastAPI. 
It provides basic CRUD (Create, Read, Update, Delete) operations for tasks and includes real-time updates for task status changes via WebSocket.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Testing with SwaggerUI](#testing-the-api-with-swagger-ui)
- [Performance Testing](#performance-testing)


## Features

####  Task Management
- Full CRUD operations for tasks (Create, Read, Update, Delete)
- Role Based Access Control (RBAC)
- Real-time task status updates via WebSocket

####  Authentication & Security

- Secure password hashing (bcrypt)
- OAuth2 authentication with access and refresh tokens
- Generation of a new access token based on refresh token
- Refresh token rotation
- Brute-force protection via Redis rate limiting
- Replay attack prevention via used token tracking and validation
- Automatic cleanup of expired and used tokens via scheduled cron job
- Logout with refresh token invalidation

####  Architecture
- Clean architecture: 
  - Presentation layer (endpoints)
  - Business logic (services)
  - Infrastructure (Unit Of Work + Repositories)
- Async SQLAlchemy + Alembic migrations
- Modular FastAPI project structure


## Project Structure

The project follows the following directory structure:

```
task_manager_fastapi/
├── alembic/
├── grafana/
├── src/
│   ├── api/
│   │   ├── dependencies/
│   │   ├── endpoints/
│   │   ├── middleware/
│   │   ├── schemas/
│   ├── core/
│   ├── db/
│   ├── exceptions/
│   ├── loggers/
│   ├── repositories/
│   ├── services/
│   ├── tests/
│   │   ├── integration_tests/
│   │   ├── load
│   │   ├── unit_tests/
│   ├── utils/
│   ├── websockets/
├── .dockerignore
├── .env
├── .gitignore
├── alembic.ini
├── docker-compose.override.yml
├── docker-compose.yml
├── Dockerfile
├── loki-config.yaml
├── main.py
├── migrate.sh
├── prometheus.yml
├── promtail-config.yaml
├── pytest.ini
├── README.md
├── requirements.txt
```

- `alembic`: Database migration files.
- `grafana`: Monitoring dashboard for visualizing metrics and logs.
- `src`: Contains the main application code.
  - `api`: API-related logic.
    - `dependencies`: FastAPI dependencies.
    - `endpoints`: Task, user, authentication and websocket API routes.
    - `middleware`: Middleware for simple logging.
    - `schemas`: Pydantic models for request/response validation.
  - `core`: Core configurations.
  - `db`: Database configuration and models.
  - `exceptions`: Custom exception handlers.
  - `loggers`: Logger configurations.
  - `repositories`: Data access layer (CRUD operations).
  - `services`: Business logic layer.
  - `tests`: Integration and unit tests.
    - `integration_tests`: Integration tests covering multiple components working together.
    - `load`: Load testing scripts.
    - `unit_tests`: Unit tests for isolated functions and classes.
  - `utils`: Helper functions and utilities.
  - `websockets`: WebSocket connection handling and logic.
- `.dockerignore`: Specifies files to exclude from the Docker context.
- `.env`: Store environment variables.
- `.gitignore`: Lists files and directories to be ignored by version control.
- `alembic.ini`: Alembic configuration.
- `docker-compose.override.yml`: Overrides default Docker Compose settings for development.
- `docker-compose.yml`: Defines and runs multi-container Docker applications.
- `Dockerfile`: Instructions for building the Docker image.
- `loki-config.yaml`: Configuration file for Grafana Loki log aggregation.
- `main.py`: Application entry point.
- `migrate.sh`: Shell script to run database migrations.
- `prometheus.yml`: Configuration for Prometheus metrics collection.
- `promtail-config.yaml`: Configuration for Promtail log shipping to Loki.
- `pytest.ini`: Tests configuration.
- `README.md`: Project documentation (overview, setup, usage).
- `requirements.txt`: List of project dependencies.


### API Endpoints

The API exposes the following endpoints:

- `POST /api/v1/auth/register/`: Register a new user.
- `POST /api/v1/auth/login/`: Authenticate and receive JWT access and refresh tokens.
- `POST /api/v1/auth/refresh/`: Create a new access token and rotate refresh token.
- `POST /api/v1/auth/sessions/`: Retrieve all user sessions.
- `POST /api/v1/auth/logout/`: Log out the user.
- `POST /api/v1/auth/logout_all/`: Log out all user sessions.
- `GET /api/v1/users/about_me/`: Retrieve user info.
- `GET /api/v1/tasks/`: Retrieve a list of tasks.
- `POST /api/v1/tasks/`: Create a new task.
- `GET /api/v1/tasks/{task_id}`: Retrieve a specific task. 
- `PUT /api/v1/tasks/{task_id}`: Update a specific task.
- `DELETE /api/v1/tasks/{task_id}`: Delete a specific task. 

For real-time updates on task status changes, use WebSocket connections to `/ws/tasks/{client_id}`.


## Testing the API with Swagger UI

Fast API comes with Swagger UI. This tool is automatically generated based on your API's route definitions and Pydantic models.

### Accessing Swagger UI

Once the API is running, Swagger UI can be accessed on the following URL:

```bash
http://localhost:8000/docs
```

You can use swagger UI to:

1. **Browse Endpoints**
2. **Send Requests**
3. **View Responses**
4. **Test Validations**

**To Test with SwaggerUI, you can do the following for each endpoint explained above**

1. Open your web browser and navigate to the /docs path as mentioned above.

2. Explore the available endpoints and select the one you want to test.

3. Click on the "Try it out" button to open an interactive form where you can input data.

4. Fill in the required parameters and request body (if applicable) according to the API documentation given above.

5. Click the "Execute" button to send the request to the API.

6. The response will be displayed below, showing the status code and response data.

7. You can also view example request and response payloads, which can be helpful for understanding the expected data format.


## Performance Testing

### Test Environment
- Docker (isolated environment with limited resources):
  - Hardware: Lenovo ThinkPad E16  
  - CPU: 4 vCPUs (Intel Core i7-13700H @ 2.4 GHz per core)  
  - RAM: 2 GB  
- Workers: 4 Uvicorn workers  
- Stack: FastAPI + async PostgreSQL (no caching)

### Load Test Configuration
- Concurrent users: 300 (using Locust)  
- Ramp-up rate: 5 users per second  
- Maximum load: approximately 150 requests per second (RPS)

### Results
| Metric                   | Value           |
|--------------------------|-----------------|
| Average response time     | 11 ms           |
| 95th percentile latency   | 20 ms           |
| Max response time        | ~280 ms          |
| Failure rate             | < 0.01%         |
| Average throughput (RPS)  | 150             |

### Conclusion
The application demonstrates stable performance under high load with limited resources, maintaining low latency and minimal errors.



