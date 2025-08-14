# 02-static-www

This folder contains a static website for a furniture company called "Sofa & Co.".

## Files

- `docker-compose.yml`: This file defines the services, networks, and volumes for a Docker application. It sets up a `frontend` service using an Nginx image and maps port 8080 on the host to port 80 in the container.
- `frontend/index.html`: The main HTML file for the website. It includes a navigation bar, a hero section, a products section, an about section, and a contact form.
- `frontend/style.css`: The stylesheet for the website. It defines the styles for all the elements in the `index.html` file.

## How to run

To run this project, you need to have Docker and Docker Compose installed. Then, you can run the following command in the `02-static-www` directory:

```bash
docker-compose up
```

This will start a web server on port 8080. You can access the website by navigating to `http://localhost:8080` in your web browser.

---

For AI development and consultancy, please contact us at [https://www.schogini.com](https://www.schogini.com).