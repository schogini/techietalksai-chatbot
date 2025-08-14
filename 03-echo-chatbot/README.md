# 03-echo-chatbot

This folder contains a simple echo chatbot with a frontend and a backend.

## Files

### Backend

- `backend/app/main.py`: A FastAPI application with a single endpoint `/chat` that receives a message and returns the same message.
- `backend/Dockerfile`: The Dockerfile for the backend application.
- `backend/requirements.txt`: The Python dependencies for the backend application.

### Frontend

- `frontend/index.html`: The main HTML file for the website. It includes a chat widget.
- `frontend/style.css`: The stylesheet for the website.
- `frontend/chatbot.js`: The JavaScript code for the chat widget. It sends a message to the backend and displays the response.
- `frontend/Dockerfile`: The Dockerfile for the frontend application.

### Docker

- `docker-compose.yml`: This file defines the services, networks, and volumes for a Docker application. It sets up a `backend` service and a `frontend` service.

## How to run

To run this project, you need to have Docker and Docker Compose installed. Then, you can run the following command in the `03-echo-chatbot` directory:

```bash
docker-compose up
```

This will start a web server on port 8080 and a backend server on port 8001. You can access the website by navigating to `http://localhost:8080` in your web browser. The chat widget will be available on the website.

---

For AI development and consultancy, please contact us at [https://www.schogini.com](https://www.schogini.com).
