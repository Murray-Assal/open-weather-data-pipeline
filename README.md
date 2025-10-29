# Open Weather Data Pipeline
A weather‑forecast data ETL pipeline to extract, clean and store it in a Postgres data warehouse.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Pipeline](#running-the-pipeline)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Technologies](#technologies)
- [Contribution](#Contribution)
- [Contact](#contact)

## Overview
This project implements a data pipeline that:
1. **Extracts** weather forecast data from an API (or other source).
2. **Transforms / Cleans** the data (e.g., parsing, filtering, sanitising).
3. **Loads** it into a PostgreSQL‑based data warehouse for analytics, reporting or downstream uses.

It is designed as a reproducible, easy‑to‑deploy solution (via Docker & docker‑compose) so you can spin up the full environment with minimal setup.

## Features
- Modular ETL code structure (extract → transform → load).
- Use of Docker + docker‑compose for environment isolation and reproducibility.
- Configuration via `.env` and `config/` directory.
- Logs directory for pipeline run history.
- Postgres data warehouse (`pgdata/` directory holds data files) for storing cleaned weather data.
- DAGs folder (if using a scheduler like Apache Airflow) to manage workflows.

## Architecture
Below is a high‑level view of how the pipeline works:

```
Weather API  ───>  Extract  ───>  Transform/Clean  ───>  Load into PostgreSQL
                (Python code)          (Python code)              (SQL/DWH)
```

And in deployment:
- A Docker container runs the ETL job (or an orchestrator triggers the job).
- Postgres is also containerised and serves as the data warehouse.
- Logs and configuration are maintained locally.

## Getting Started

### Prerequisites
- Docker & docker‑compose installed on your system.
- A free API key from your weather data provider (if required).
- Basic knowledge of command line, Python, and Postgres.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Murray-Assal/open-weather-data-pipeline.git
   cd open-weather-data-pipeline
   ```
2. Build and start the Docker containers:
   ```bash
   docker-compose up --build
   ```
   This will pull/build the necessary images and start the pipeline + Postgres.

### Configuration
- Copy the `.env.example` to `.env` (if provided) and fill in your environment variables (e.g., API key, Postgres password, database name).
- In the `config/` folder, locate files such as `pipeline_config.yml` (if present) and update settings (e.g., API endpoints, schedule, target tables).
- Ensure volumes (e.g., `pgdata/`, `logs/`) have correct permissions.

### Running the Pipeline
- With Docker‑Compose running, the ETL job should trigger (manually or via scheduler).
- To run manually:
  ```bash
  docker-compose run --rm pipeline python run_pipeline.py
  ```
  (Adjust the command according to the actual entrypoint script.)
- After running, check:
  - `logs/` to log dag runs.
  - In Postgres: connect via `psql` or a GUI tool and inspect the tables populated under the target database.

## Usage
Once the data is loaded into Postgres, you can:
- Run SQL queries to generate weather trends, summaries, and reports.
- Hook into the data warehouse for BI dashboards (e.g., using Metabase or Tableau).
- Extend the pipeline to ingest other data sources (e.g., historical weather, additional geographies).
- Schedule the pipeline (e.g., daily, hourly) using Airflow, cron or other orchestration.

## Directory Structure
Here’s a quick rundown of key folders:
```
config/        # Configuration files (API endpoints, pipeline settings)
dags/          # DAG definitions (if using Airflow)
logs/          # Logging output from ETL runs
pgdata/        # Persistent Postgres data files (for local dev)
.dockerfile    # Dockerfile for pipeline container
docker-compose.yaml  # Composition of pipeline + Postgres services
requirements.txt     # Python dependencies
```

## Technologies
- Python (ETL scripts)
- PostgreSQL (as data warehouse)
- Docker / docker‑compose (containerisation)
- Airflow for scheduling
- YAML / JSON / .env for configuration

## Contributing
Contributions are welcome! If you’d like to:
1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature‑xyz`).
3. Make your changes & write tests (if relevant).
4. Submit a Pull Request, describing the change and the reason.
5. Please follow the existing code style and include documentation for any new modules.

## Contact
Created by [Murray Assal](https://github.com/Murray-Assal) – feel free to open issues or reach out for questions.

