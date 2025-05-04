# FastAPI Task Manager 
Real-time task manager

FastAPI Task Manager is a simple task management API built using FastAPI. 
It provides basic CRUD (Create, Read, Update, Delete) operations for tasks and includes real-time updates for task status changes via WebSocket.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Testing with SwaggerUI](#testing-the-api-with-swagger-ui)




## Features

- User registration and authentication.
- CRUD operations for tasks (Create, Read, Update, Delete).
- Real-time updates for task status changes using WebSocket.
- OAuth2 authentication for API access.


## Project Structure

The project follows the following directory structure:

```
task_manager_fastapi/
├── alembic/
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
│   ├── utils/
│   ├── websockets/
├── .env
├── .gitignore
├── alembic.ini
├── main.py
├── README.md
├── requirements.txt
```

- `src`: Contains the main application code.
  - `alembic`: Database migration files.
  - `api`: Contains API endpoints for tasks, users, authentication and websockets.
    - `endpoints`: Task, user, authentication and websocket API endpoints.
    - `middleware`: Middleware for simple logging.
    - `schemas`: Pydantic models for request and response.
  - `core`: Core configurations.
  - `db`: Database configuration and models.
- `.env`: Store environment variables.
- `.gitignore`: Lists files and directories to be ignored by version control.
- `alembic.ini`: Alembic configuration.
- `README.md`: Documentation about the project.
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
