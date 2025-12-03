# React, FastAPI, and PostgreSQL Stack DevOps Pipeline 

## 🙌 Acknowledgements

- **Helped & Guided By:** [Jinna Balu](https://jinnabalu.com/)
- **Forked From:** [Original Project Name]
- **Purpose:**  
  This project is built for **learning**, **experimentation**, and to **demonstrate DevOps capabilities**.  
  Not intended for production use. 

## Dev Machine Instructions 

- [Installation Instructions](INSTALLATION-INSTRUCTIONS.md)

## DevOps Learning Activity
### 1. .gitignore Update 

**Usecase** : .gitignore was very basic and need to be add with MERN Stack related ignorable configuartioin

**Solution** : 
  - Generated `.gitignore` file using [toptal gitignore generator](https://www.toptal.com/developers/gitignore) for visualstudiocode,react,node

### 2. Dockerise Frontend and Backend
**Usecase** : Running frontend and backend manually required multiple setups and dependencies, making deployments inconsistent.
**Solution** : Created Dockerfiles for both frontend (React) and backend (Node/Express). Built isolated images that bundled dependencies, enabling uniform and reproducible builds across environments.
- [Dockerfiles for both Frontend and Backend to Build Images ](MERN-Stack.git/)


### 3. Create Docker Compose for MongoDB
**Use Case** : The backend required a running MongoDB service. Running MongoDB manually was repetitive and error-prone.

**Solution** : Wrote a docker-compose.yml file to spin up MongoDB + backend + frontend together. This ensured easy orchestration and networking between containers.
- [Docker-compose.yml File to run as a orchestration](MERN-Stack.git/)

### 4. Buid the Docker Image Locally 
**Use case** : Needed to test the application in a containerized environment before pushing to cloud or registry.

**Solution** : Built Docker images locally using docker build and tested them by running containers. Debugged issues like dependency mismatches before moving to CI/CD.
- [Instructions For running  ]

### 5. Buid the Docker Image with GitHub Actions and Push to vercel.com

**Use Case** : Manual builds weren’t scalable. Needed automation for continuous integration and deployment.

**Solution** : Configured a GitHub Actions workflow that built Docker images on every push, then pushed them to Google Container Registry (GCR). This automated container publishing.

### 6. Run Application Locally 
**Use Case** : Before deploying to cloud, needed to validate that the app runs smoothly with containers locally.

**Solution** : Used docker-compose up to run frontend, backend, and MongoDB together on localhost. Verified functionality via API and frontend testing.

### 7. Run Application On AWS EC2
**Use Case** : To simulate production, needed to host the app in a cloud VM.

**Solution** : Provisioned an AWS EC2 instance, installed Docker & Docker Compose, and deployed the app. This validated cloud readiness and environment configs.

## Security 

### 8. Quality Gate or Code Quality Check with SonarQube
**Use Case** : Needed to identify code smells, bugs, and maintainability issues early.

**Solution** : Integrated SonarQube in the pipeline for static code analysis, setting up a Quality Gate to block builds failing checks.

### 9. Quality Gate or Code Quality Check with DeepSource
**Use Case** : Secrets (API keys, tokens) could be accidentally pushed into repos.

**Solution** : Configured git-secrets and gitleaks to scan repos during commits/CI pipeline, preventing secrets leakage.

### 10. Secrets Scan (open source tool)
**Use Case** : Secrets (API keys, tokens) could be accidentally pushed into repos.

**Solution** : Configured git-secrets and gitleaks to scan repos during commits/CI pipeline, preventing secrets leakage.

### 11. Vulnerability Scans with Dependence Track  to Create SBOM
**Use Case** : Needed visibility into third-party dependencies and potential CVEs.

**Solution** : Used Dependency-Track to generate an SBOM (Software Bill of Materials) and continuously scan for vulnerabilities in dependencies.
- https://dependencytrack.org/

### 12. OWASP Top 10 Scan with Arachni
**Use Case** : To check application security against common OWASP Top 10 risks (XSS, SQL injection, CSRF, etc.).

**Solution** : Configured Arachni scan engine to scan app endpoints and report vulnerabilities, strengthening security posture.
- https://github.com/Arachni/arachni

##  Observebility Instrumentation 

### 13. Centralised Logging with ELK Stack 
**Use Case** : Logs were scattered across containers, making debugging difficult.

**Solution** : Deployed ELK (Elasticsearch, Logstash, Kibana) to centralize logs from frontend, backend, and MongoDB into one dashboard.
### 14. Monetering and Alterting () with prometheus , Grafana 
**Use Case**: Needed real-time metrics on CPU, memory, and app health.

**Solution**: Configured Prometheus for metrics scraping and Grafana dashboards with alerts for performance monitoring.
### 15. Uptime and Application Status with Uptime Kuma
**Use Case** : Required a simple way to monitor uptime and alert on downtime.

**Solution** : Set up Uptime Kuma via Docker to continuously check service availability and generate status dashboards.
- https://uptimekuma.org/install-uptime-kuma-docker/

### 16. Tracing with Elastic APM or Jaeger
**Use Case** : Microservices made it difficult to trace latency issues and bottlenecks.

**Solution** : Integrated Elastic APM and Jaeger for distributed tracing, allowing visibility into request flows across services.
- https://www.jaegertracing.io/

 
> Unofficial Dockerized version of [Idurar ERP CRM](https://github.com/idurar/idurar-erp-crm) for educational and DevSecOps learning purposes.

This project provides a Dockerized setup for the open-source [Idurar ERP CRM](https://github.com/idurar/idurar-erp-crm) application.  
It includes Docker support, CI/CD workflows, and is designed for experimenting with containerization and security audits.

---

## Security & Source Warning

- Always trust official builds from: [https://idurarapp.com](https://idurarapp.com)
- Official repo: [https://github.com/idurar/idurar-erp-crm](https://github.com/idurar/idurar-erp-crm)
- Do **NOT** run versions downloaded from unofficial GitHub repos in production. They may be **fake**, **modified**, or **malicious**.
- This repository is for educational purposes only. Not affiliated with the official Idurar team.

---

### Features

- Docker support (frontend & backend)
- Docker Compose for full app orchestration
- GitHub Actions CI/CD Workflow
- DevSecOps tools integration ready (e.g., Trivy, SonarQube, etc.)

---

### Getting Started

```bash
# Clone this repo
git clone https://github.com/venkateshkallu/Idurur-dockerized.git

# Navigate to project
cd Idurur-dockerized

# Start Docker containers
docker-compose up --build
```

```arduino
Folder Structure

Idurur-dockerized/
├── backend/               → Node.js API
├── frontend/              → React (Ant Design) UI
├── docker-compose.yml     → Multi-container setup
├── Dockerfile             → Backend Dockerfile
├── .github/workflows/     → GitHub Actions for CI/CD
```

## Credits
This project is built upon the amazing work of the Idurar team:

Official project: https://github.com/idurar/idurar-erp-crm

Original license: GNU Affero General Public License v3.0

All ERP/CRM app features (Invoice, Customer, Quote, etc.) are developed by Idurar.
This project only adds Dockerization, automation, and DevSecOps improvements.

## Use Cases
Learn Docker with a real-world full-stack app

Test CI/CD using GitHub Actions

Experiment with security scanning (SCA, SAST tools)

Practice DevOps & DevSecOps workflows

### License
This repository and the original Idurar code are licensed under:

GNU Affero General Public License v3.0
See LICENSE for details.

### Show Your Support
If you found this helpful, please consider:

- Starring this repo

- Forking and experimenting

- Sharing feedback


