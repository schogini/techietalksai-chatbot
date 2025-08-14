# 01-env-setup

This folder contains a basic setup for a web server using Docker.

## Files

- `docker-compose.yml`: This file defines the services, networks, and volumes for a Docker application. It sets up a `frontend` service using an Nginx image and maps port 8080 on the host to port 80 in the container.
- `frontend/index.html`: A simple HTML file that displays a "Hello, World!" message.

## How to run

To run this project, you need to have Docker and Docker Compose installed. Then, you can run the following command in the `01-env-setup` directory:

```bash
docker-compose up
```

This will start a web server on port 8080. You can access the "Hello, World!" page by navigating to `http://localhost:8080` in your web browser.

---

For AI development and consultancy, please contact us at [https://www.schogini.com](https://www.schogini.com).