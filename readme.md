# Deployment Documentation

## Project Overview

This document provides instructions for deploying the News Article Scraper Data Pipeline project. The project, authored by Shashak, consists of a Node.js backend for API service with MySQL as the database. The project repository is hosted on GitHub at [NewsArticleMiner](https://github.com/shashankmadhura/NewsArticleMiner).

### Project Details

- **Author Name:** Shashank
- **GitHub Repository:** [NewsArticleMiner](https://github.com/shashankmadhura/NewsArticleMiner)
- **Backend Technology:** Node.js, Python3
- **Database:** MySQL

## Deployment Steps

### 1. Clone the Repository

Clone the project repository from the GitHub repository:

```bash
git clone https://github.com/shashankmadhura/NewsArticleMiner.git
```

### 2. Build and Deploy with Docker Compose

Navigate to the project directory and use Docker Compose to build and deploy the project:

```bash
cd NewsArticleMiner
docker-compose build
docker-compose up -d
```

The above commands will build the Docker images and deploy the containers in detached mode (`-d`). The API service will be accessible at port 3000.

### 3. Verify Deployment

Once the deployment is complete, you can verify it by accessing the API service. Visit `http://localhost:3000` (or the appropriate URL) to access the API documentation and test the endpoints.

### 4. Shutdown

To stop and remove the containers, use the following command:

```bash
docker-compose down
```

## Additional Information

- **Data Pipeline Code:** The `pipeline.py` file contains the code related to the data pipeline.
- **Backend API Code:** The `backend` folder contains all the Node.js API code.
- **API Documentation:** Detailed API documentation is available at [Postman](https://documenter.getpostman.com/view/12590131/2sA358c5Q5).

For additional assistance or inquiries, please refer to the project repository or contact the project author.
```

This deployment documentation provides a concise guide for deploying the project using Docker Compose and includes links to the GitHub repository and API documentation for further reference.