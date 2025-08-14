# 04-agentic-chatbot

This folder contains an agentic chatbot that uses the `agno` library.

## Files

### Backend

- `backend/app/main.py`: A FastAPI application that uses the `agno` library to create an agentic chatbot. The agent is configured with a model, instructions, and knowledge bases. The agent can search the web and its knowledge bases to answer questions.
- `backend/Dockerfile`: The Dockerfile for the backend application.
- `backend/requirements.txt`: The Python dependencies for the backend application.

### Frontend

- `frontend/index.html`: The main HTML file for the website. It includes a chat widget.
- `frontend/style.css`: The stylesheet for the website.
- `frontend/chatbot.js`: The JavaScript code for the chat widget. It sends a message to the backend and displays the response.
- `frontend/Dockerfile`: The Dockerfile for the frontend application.

### Docker

- `docker-compose.yml`: This file defines the services, networks, and volumes for a Docker application. It sets up a `backend` service and a `frontend` service.
- `.env`: This file contains the API keys for OpenAI, DeepSeek, and Gemini.

## How to run

To run this project, you need to have Docker and Docker Compose installed. You also need to have API keys for OpenAI, DeepSeek, and Gemini in the `.env` file.

Then, you can run the following command in the `04-agentic-chatbot` directory:

```bash
docker-compose up
```

This will start a web server on port 8080 and a backend server on port 8001. You can access the website by navigating to `http://localhost:8080` in your web browser. The chat widget will be available on the website.

---

For AI development and consultancy, please contact us at [https://www.schogini.com](https://www.schogini.com).
