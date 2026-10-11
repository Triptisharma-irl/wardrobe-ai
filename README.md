# Distributed Job Scheduler (Kafka-based)

A working simulation of a distributed job scheduler, built on real Apache
Kafka running locally via Docker. Demonstrates job scheduling, a
Kafka-backed job queue, multiple distributed workers consuming jobs in
parallel, and a retry service with exponential backoff.

## Architecture
- **Scheduler Service** (`scheduler.py`) — creates jobs and publishes them
  to the Kafka topic `job-queue`.
- **Job Queue** — a real Kafka topic (`job-queue`), running via Docker.
- **Worker Service** (`worker.py`) — consumes jobs from Kafka. Multiple
  worker instances share a Kafka consumer group, so Kafka automatically
  load-balances jobs across them (this is what real distributed workers
  look like).
- **Retry Service** — built into the worker: failed jobs are re-published
  to the topic with exponential backoff, up to `max_retries`.

## How to run it locally

### 1. Install Docker Desktop
Download from https://www.docker.com/products/docker-desktop/ if not
already installed.

### 2. Start Kafka + Zookeeper
```bash
docker-compose up -d
```
Wait ~20-30 seconds for Kafka to be ready.

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Start 2-3 workers (in separate terminal tabs)
```bash
python worker.py 1
python worker.py 2
python worker.py 3
```

### 5. Run the scheduler to submit jobs
```bash
python scheduler.py
```

You'll see jobs being distributed across the different workers in
real time, with retries happening automatically on simulated failures.

### 6. Stop everything
```bash
docker-compose down
```

## Why this design
This mirrors the core ideas behind real distributed job schedulers
(like the ones used at large tech companies): a durable queue (Kafka)
decouples job submission from execution, multiple workers process jobs
in parallel via a shared consumer group, and failures are retried with
backoff instead of being lost.
