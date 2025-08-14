# 07-cors-security

This folder contains an agentic chatbot that uses the `agno` library, a RAG vector knowledge base, and CORS security.

## Files

### Backend

- `backend/app/main.py`: A FastAPI application that uses the `agno` library to create an agentic chatbot. The agent is configured with a model, instructions, and a combined knowledge base. The knowledge base is created from CSV files, PDF URLs, websites, and local PDF files. The knowledge base is stored in a LanceDB vector database. The backend also has CORS middleware to allow requests from specific origins.
- `backend/Dockerfile`: The Dockerfile for the backend application.
- `backend/requirements.txt`: The Python dependencies for the backend application.
- `backend/data`: This directory contains the data for the knowledge base.
- `backend/tmp`: This directory contains the LanceDB vector database.

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

Then, you can run the following command in the `07-cors-security` directory:

```bash
docker-compose up
```

This will start a web server on port 8080 and a backend server on port 8001. You can access the website by navigating to `http://localhost:8080` in your web browser. The chat widget will be available on the website.

---

For AI development and consultancy, please contact us at [https://www.schogini.com](https://www.schogini.com).
