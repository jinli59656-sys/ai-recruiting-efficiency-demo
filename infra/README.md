# Local Infrastructure

This project uses `docker compose` to manage local middleware services.

## Current services

- `minio`: stores original resume files
- `minio-init`: creates the default bucket after MinIO starts

## Start

From the project root:

```powershell
docker compose up -d
```

Check status:

```powershell
docker compose ps
```

Check MinIO logs:

```powershell
docker compose logs -f minio
```

Stop all services:

```powershell
docker compose down
```

Stop services and remove volumes:

```powershell
docker compose down -v
```

## MinIO access

- API endpoint: `http://localhost:9000`
- Console: `http://localhost:9001`
- Default bucket: `resume-files`
- Default username: `minioadmin`
- Default password: `minioadmin123`

You can override these values with shell environment variables before running `docker compose up -d`.

## Backend config

The backend should connect to MinIO with:

- `MINIO_ENDPOINT=localhost:9000`
- `MINIO_ACCESS_KEY=minioadmin`
- `MINIO_SECRET_KEY=minioadmin123`
- `MINIO_SECURE=false`
- `MINIO_BUCKET=resume-files`

The backend keeps running on the host machine for now. Only the middleware runs in Docker.

## Add Kafka later

When Kafka is introduced, add a new `kafka` service to [docker-compose.yml](/D:/桌面存储内容/培训/project/hr-assistant/docker-compose.yml) with:

- an image
- exposed ports
- required environment variables
- a persistent volume

Then add backend env vars such as:

- `KAFKA_BOOTSTRAP_SERVERS=localhost:9092`
- `KAFKA_RESUME_PARSE_TOPIC=resume.parse`

## Add Milvus later

When vector storage is introduced, add a new `milvus` stack to [docker-compose.yml](/D:/桌面存储内容/培训/project/hr-assistant/docker-compose.yml). Milvus usually requires multiple services depending on the chosen deployment mode, so keep it isolated as its own compose section.

Then add backend env vars such as:

- `MILVUS_HOST=localhost`
- `MILVUS_PORT=19530`
- `MILVUS_COLLECTION=resumes`

## Recommended workflow

1. Start MinIO with Docker.
2. Connect FastAPI to MinIO through backend env vars.
3. Upload resume files to MinIO.
4. Publish a Kafka message after upload succeeds.
5. Consume the message in an async parser worker.
6. Write parsed vectors into Milvus.
