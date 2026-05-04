# YouTube Channel ELT Pipeline

An end-to-end ELT pipeline that extracts video statistics from a YouTube channel via the YouTube Data API v3, loads the raw data into a PostgreSQL data warehouse, and validates it with Soda Core — all orchestrated by Apache Airflow running on Docker.

## Architecture

```
YouTube Data API v3
        │
        ▼
  Extract & save JSON          (produce_json DAG — daily at 14:00 UTC)
        │
        ▼
  Load → staging → core        (update_db DAG — triggered automatically)
        │
        ▼
  Soda data quality checks     (data_quality DAG — triggered automatically)
```

### DAGs

| DAG | Schedule | Description |
|-----|----------|-------------|
| `produce_json` | `0 14 * * *` | Calls YouTube API, saves raw JSON to `./data/` |
| `update_db` | triggered | Loads JSON into `staging` and `core` PostgreSQL schemas |
| `data_quality` | triggered | Runs Soda scans on both schemas |

## Project Structure

```
youtube_project/
├── dags/
│   ├── api/video_stats.py        # YouTube API helpers
│   ├── data_quality/soda.py      # Soda scan operator wrapper
│   └── data_warehouse/main.py    # DAG definitions
├── include/
│   └── soda/
│       ├── checks.yml            # Soda quality checks
│       └── configuration.yml     # Soda datasource config
├── tests/
│   ├── conftest.py
│   ├── unit_test.py
│   └── integration_test.py
├── data/                         # JSON output (gitignored)
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── .env.example
```

## Prerequisites

- Docker & Docker Compose
- A [YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com) key

## Setup

1. **Clone the repo and copy the env file**

   ```bash
   git clone <repo-url>
   cd youtube_project
   cp .env.example .env
   ```

2. **Fill in `.env`**

   ```env
   # YouTube
   YOUTUBE_API_KEY=your_api_key_here
   CHANNEL_HANDLE=@YourChannelHandle

   # Airflow
   AIRFLOW_UID=50000
   AIRFLOW_WWW_USER_USERNAME=airflow
   AIRFLOW_WWW_USER_PASSWORD=airflow
   FERNET_KEY=your_fernet_key

   # Docker Hub (custom Airflow image)
   DOCKERHUB_NAMESPACE=your_namespace
   DOCKERHUB_REPOSITORY=your_repo

   # PostgreSQL
   POSTGRES_CONN_HOST=postgres
   POSTGRES_CONN_PORT=5432
   POSTGRES_CONN_USERNAME=postgres
   POSTGRES_CONN_PASSWORD=postgres

   METADATA_DATABASE_NAME=airflow
   METADATA_DATABASE_USERNAME=airflow
   METADATA_DATABASE_PASSWORD=airflow

   CELERY_BACKEND_NAME=celery
   CELERY_BACKEND_USERNAME=celery
   CELERY_BACKEND_PASSWORD=celery

   ELT_DATABASE_NAME=yt_elt
   ELT_DATABASE_USERNAME=yt_user
   ELT_DATABASE_PASSWORD=yt_password
   ```

3. **Build and start the stack**

   ```bash
   docker compose up --build
   ```

4. **Open Airflow UI** at [http://localhost:8080](http://localhost:8080) and enable the `produce_json` DAG.

## Running Tests

```bash
pytest tests/
```

Dependencies: `soda-core-postgres==3.3.14`, `pytest==8.3.3`

## API Functions (`dags/api/video_stats.py`)

| Function | Description |
|----------|-------------|
| `get_playlist_id()` | Resolves a channel handle to its uploads playlist ID |
| `get_video_ids(playlist_id)` | Paginates through the playlist and returns all video IDs |
| `get_video_details(video_ids)` | Fetches title, publish date, duration, views, likes, and comments for each video |
| `save_to_json(data)` | Writes the extracted data to `./data/YT_data_<date>.json` |
