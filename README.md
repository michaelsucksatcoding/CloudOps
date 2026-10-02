# CloudOps AI

> **Bahasa:** [English](#cloudops-ai) | [Bahasa Indonesia](#cloudopsai-bahasa-indonesia)

Cloud-Native Intelligent Operations Platform.

CloudOps AI is a Python-first platform for collecting application/infrastructure telemetry, processing it through an event-driven pipeline, detecting anomalous behaviour with machine learning, and exposing service health, analytics, incidents, and recommendations through an API/dashboard.

The platform targets **no cloud provider**. It runs on Docker Compose and, optionally, on any generic local Kubernetes cluster (kind, k3d, minikube).

## Architecture

```text
Applications / Simulator
        │
        ▼
   FastAPI / POST /events
        │
        ├──► PostgreSQL  (durable system of record)
        │         │
        │         ▼
        │   event-processor worker  (created_at watermark polling)
        │         │
        │         ▼
        │   TelemetryProcessor
        │      ├──► Hot storage
        │      └──► Data lake
        │              │
        │              ▼
        │        Analytics / ETL
        │              │
        ▼              ▼
   API + ML (Isolation Forest)
        │
        ▼
  Prometheus / Grafana
```

**Event processing.** The API validates and persists every telemetry event to PostgreSQL before publishing it to a process-local producer. A long-lived worker consumes the durable rows and routes them into hot storage and the data lake. This replaced an earlier managed-stream (queue + serverless consumer) architecture; the capability that was given up is documented openly in
[docs/architecture/event-processing.md](docs/architecture/event-processing.md) and
[ADR 0005](docs/decisions/0005-cloud-neutral-architecture.md).

## Project Status

CloudOps AI implements:

- Python/FastAPI application with Pydantic-validated telemetry ingestion
- PostgreSQL persistence (SQLAlchemy + Alembic)
- Database-backed event processing worker with hot/data-lake routing
- ML anomaly detection with Isolation Forest
- Simulator-based controlled incident evaluation with reproducible results
- Prometheus/Grafana observability
- Docker Compose as the primary runtime; Helm chart for generic local Kubernetes
- CI with automated quality gates (pytest, ruff, mypy, pip-audit, Trivy)

### Verified local state

The full stack was validated end to end on a single machine with no cloud
account and no credentials:

- Alembic migration applied; FastAPI API healthy with database connectivity confirmed
- `POST /events` and `GET /events` persist and return telemetry
- Event worker confirmed routing persisted events into hot storage and the data lake
- Prometheus scraping API metrics; Grafana datasource and all three dashboards loaded
- ML evaluation runs as a one-shot job and reproduces the committed baseline
- All eight incident scenarios execute

### Evaluation

The ML evaluation uses synthetic simulator ground truth. The committed baseline
achieves **F1 = 0.8719** with a high false-positive rate of **0.88** — a
documented negative result indicating training-data distribution mismatch. See
[docs/evaluation/](docs/evaluation/) for methodology, results, reproducibility,
and limitations. Local ML runs may report a higher F1 on the evaluation set;
neither figure should be presented as production validation.

This project is an academic final-year project artifact. It is **not**
production-ready, and synthetic simulator evaluation must not be described as
production validation.

---

## Quickstart & Local Development

### 1. Setup Virtual Environment

```bash
python -m venv .venv
```

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 3. Run Quality Checks

```bash
ruff check . && ruff format --check . && mypy services && pytest
```

### 4. Run API Locally

```bash
alembic upgrade head
uvicorn services.api.app.main:app --reload
```

### 5. Run Simulator

```bash
python -m services.simulator.telemetry
```

---

## Containerization & Docker (Primary Runtime)

Run the complete local multi-container stack:

```bash
docker compose up --build
```

This starts six services:

| Service | Purpose | Port |
|---|---|---|
| `api` | FastAPI (runs Alembic migrations, then serves) | 8000 |
| `postgres` | PostgreSQL 16 durable system of record | 5432 |
| `event-processor` | Long-lived telemetry consumer worker | — |
| `ml` | One-shot train + evaluate job, then exits | — |
| `prometheus` | Metrics scraping and alerting | 9090 |
| `grafana` | Dashboards (admin/admin locally) | 3000 |

Build individual images:

```bash
docker build --target api -t cloudops-api:local .
docker build --target ml -t cloudops-ml:local .
docker build --target event-processor -t cloudops-event-processor:local .
```

Verify the API:

```bash
curl http://localhost:8000/health
```

Stop the stack:

```bash
docker compose down
```

---

## Kubernetes & Helm (Secondary, Generic Local Cluster)

The chart targets any generic local Kubernetes cluster. `values.yaml` is the
canonical configuration and contains no cloud-provider assumptions: no cloud
identity binding, no cloud ingress controller, no cloud block storage class, and
no managed-service wiring. All services are `ClusterIP`; ingress is **disabled by
default**.

### 1. Create a Local Cluster

```bash
# kind
kind create cluster --name cloudops

# k3d
k3d cluster create cloudops
```

### 2. Build Images into the Cluster

```bash
for t in api ml event-processor; do
  docker build --target "$t" -t "cloudops-$t:local" .
  kind load docker-image "cloudops-$t:local" --name cloudops   # kind
done
```

### 3. Create Namespaces

```bash
kubectl apply -f infrastructure/kubernetes/namespaces/
```

### 4. Validate the Chart

```bash
helm lint infrastructure/kubernetes/helm/cloudops-ai
helm template cloudops-ai infrastructure/kubernetes/helm/cloudops-ai
```

### 5. Deploy

```bash
helm upgrade --install cloudops-ai infrastructure/kubernetes/helm/cloudops-ai \
  --namespace cloudops-dev \
  --create-namespace
```

### 6. Run Migrations

The API image carries Alembic but does not run migrations at startup:

```bash
kubectl exec -n cloudops-dev deploy/cloudops-ai-api -- alembic upgrade head
```

### 7. Access the Services

```bash
kubectl port-forward -n cloudops-dev svc/cloudops-ai-api 8000:8000
kubectl port-forward -n cloudops-monitoring svc/cloudops-prometheus 9090:9090
kubectl port-forward -n cloudops-monitoring svc/cloudops-grafana 3000:3000
```

### Per-Cluster Overrides

Set the StorageClass if your cluster's default is unsuitable:

```bash
helm upgrade --install cloudops-ai infrastructure/kubernetes/helm/cloudops-ai \
  --set postgres.storage.storageClass=standard
```

Enable an Ingress only if your cluster runs a controller (e.g. `nginx` for kind,
`traefik` for k3d):

```bash
helm upgrade --install cloudops-ai infrastructure/kubernetes/helm/cloudops-ai \
  --set ingress.enabled=true --set ingress.className=nginx
```

---

## CI

Continuous integration runs on every pull request and push to `main`
(`.github/workflows/ci.yml`):

- **Python Quality Gates & Security** — Ruff lint/format, Mypy, Pytest with
  coverage, PyPA `pip-audit`
- **Helm Chart & Manifest Validation** — `helm lint`, `helm template`, and a
  guard asserting the rendered output stays cloud-neutral
- **Local Docker Compose Validation** — `docker compose config`, a guard
  asserting no cloud SDK is installed, PostgreSQL health, API health, and the
  ML evaluation job
- **Container Build & Image Security Scan** — multi-target Docker build with
  buildx caching and Trivy vulnerability scanning

CI requires no cloud credentials and no registry account. There is no automated
deployment workflow: releases are run manually from a local machine.

---

## Observability

The API exposes Prometheus metrics at `GET /metrics` and returns an
`X-Request-ID` header for log correlation. The Helm chart includes a lightweight
Prometheus/Grafana stack and provisioned dashboards. See
[Observability & Monitoring](docs/architecture/observability.md) for metrics,
alerts, and local validation instructions.

---

## Project Documentation

| Document | Purpose |
|---|---|
| [AGENTS.md](AGENTS.md) | Engineering rules, commands, and scope control |
| [docs/architecture/](docs/architecture/) | Event processing, Kubernetes, observability, CI/CD |
| [docs/decisions/](docs/decisions/) | Architecture Decision Records (0003 and 0004 superseded by 0005) |
| [docs/evaluation/](docs/evaluation/) | ML methodology, results, limitations, reproducibility |

## License

MIT

---

# CloudOpsAI (Bahasa Indonesia)

> **Bahasa:** [English](#cloudops-ai) | [Bahasa Indonesia](#cloudopsai-bahasa-indonesia)

Cloud-Native Intelligent Operations Platform — Platform Operasi Cerdas Berbasis Cloud-Native.

CloudOps AI adalah platform berbasis Python yang berfungsi untuk mengumpulkan telemetri aplikasi dan infrastruktur, memprosesnya melalui pipeline berbasis event, mendeteksi perilaku anomali menggunakan machine learning, serta menampilkan health layanan, analitik, insiden, dan rekomendasi melalui API dan dashboard.

Platform ini **tidak bergantung pada penyedia cloud mana pun**. Platform ini berjalan di Docker Compose dan, secara opsional, pada cluster Kubernetes lokal generik apa pun (kind, k3d, minikube).

## Arsitektur

```text
Aplikasi / Simulator
        │
        ▼
   FastAPI / POST /events
        │
        ├──► PostgreSQL  (sistem catatan yang tahan lama)
        │         │
        │         ▼
        │   worker event-processor  (polling watermark created_at)
        │         │
        │         ▼
        │   TelemetryProcessor
        │      ├──► Hot storage
        │      └──► Data lake
        │              │
        │              ▼
        │        Analytics / ETL
        │              │
        ▼              ▼
   API + ML (Isolation Forest)
        │
        ▼
  Prometheus / Grafana
```

**Pemrosesan event.** API memvalidasi dan menyimpan setiap event telemetri ke PostgreSQL sebelum menerbitkannya ke producer di dalam proses. Worker jangka panjang mengonsumsi baris yang tahan lama dan meneruskannya ke hot storage dan data lake. Arsitektur ini menggantikan arsitektur managed-stream sebelumnya (antrean + konsumen serverless); kemampuan yang dikorbankan terdokumentasi secara terbuka di
[docs/architecture/event-processing.md](docs/architecture/event-processing.md) dan
[ADR 0005](docs/decisions/0005-cloud-neutral-architecture.md).

## Status Proyek

CloudOps AI mengimplementasikan:

- Aplikasi Python/FastAPI dengan ingestion telemetri yang divalidasi Pydantic
- Persistensi PostgreSQL (SQLAlchemy + Alembic)
- Worker pemrosesan event berbasis database dengan routing hot/data-lake
- Deteksi anomali ML dengan Isolation Forest
- Evaluasi insiden terkontrol berbasis simulator dengan hasil yang dapat direproduksi
- Observabilitas Prometheus/Grafana
- Docker Compose sebagai runtime utama; Helm chart untuk Kubernetes lokal generik
- CI dengan gerbang kualitas otomatis (pytest, ruff, mypy, pip-audit, Trivy)

### Status lokal yang telah diverifikasi

Tumpukan penuh telah divalidasi secara end-to-end pada satu mesin tanpa akun cloud dan tanpa kredensial:

- Migrasi Alembic diterapkan; API FastAPI sehat dengan konektivitas database terkonfirmasi
- `POST /events` dan `GET /events` menyimpan dan mengembalikan telemetri
- Worker event terkonfirmasi meneruskan event tersimpan ke hot storage dan data lake
- Prometheus melakukan scraping metrik API; datasource Grafana dan ketiga dashboard berhasil dimuat
- Evaluasi ML berjalan sebagai one-shot job dan mereproduksi baseline yang dikomit
- Seluruh delapan skenario insiden dapat dijalankan

### Evaluasi

Evaluasi ML menggunakan ground truth sintetis dari simulator. Baseline yang dikomit
mencapai **F1 = 0.8719** dengan false-positive rate yang tinggi sebesar **0.88** — ini
adalah hasil negatif terdokumentasi yang menunjukkan ketidaksesuaian distribusi data
latih. Lihat [docs/evaluation/](docs/evaluation/) untuk metodologi, hasil,
reproduksibilitas, dan keterbatasan. Hasil evaluasi ML lokal mungkin melaporkan F1 yang lebih
tinggi pada evaluation set; kedua angka tersebut tidak boleh disajikan sebagai validasi
produksi.

Proyek ini adalah artefak tugas akhir akademik. Proyek ini **bukan** siap untuk produksi,
dan evaluasi simulator sintetis tidak boleh digambarkan sebagai validasi produksi.

---

## Mulai Cepat & Pengembangan Lokal

### 1. Menyiapkan Virtual Environment

```bash
python -m venv .venv
```

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 2. MengInstal Dependensi

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 3. Menjalankan Pemeriksaan Kualitas

```bash
ruff check . && ruff format --check . && mypy services && pytest
```

### 4. Menjalankan API Secara Lokal

```bash
alembic upgrade head
uvicorn services.api.app.main:app --reload
```

### 5. Menjalankan Simulator

```bash
python -m services.simulator.telemetry
```

---

## Kontainerisasi & Docker (Runtime Utama)

Jalankan tumpukan lokal multi-kontainer lengkap:

```bash
docker compose up --build
```

Perintah ini memulai enam layanan:

| Layanan | Kegunaan | Port |
|---|---|---|
| `api` | FastAPI (menjalankan migrasi Alembic, lalu melayani permintaan) | 8000 |
| `postgres` | PostgreSQL 16 sebagai sistem catatan yang tahan lama | 5432 |
| `event-processor` | Worker konsumen telemetri jangka panjang | — |
| `ml` | Job training + evaluasi sekali jalan, lalu keluar | — |
| `prometheus` | Scraping metrik dan alerting | 9090 |
| `grafana` | Dashboard (admin/admin secara lokal) | 3000 |

Membangun image secara individual:

```bash
docker build --target api -t cloudops-api:local .
docker build --target ml -t cloudops-ml:local .
docker build --target event-processor -t cloudops-event-processor:local .
```

Memverifikasi API:

```bash
curl http://localhost:8000/health
```

Menghentikan tumpukan:

```bash
docker compose down
```

---

## Kubernetes & Helm (Sekunder, Cluster Lokal Generik)

Chart ini menargetkan cluster Kubernetes lokal generik apa pun. `values.yaml` adalah
konfigurasi kanonik dan tidak memuat asumsi penyedia cloud: tidak ada pengikatan identitas
cloud, tidak ada ingress controller cloud, tidak ada storage class blok cloud, dan tidak
ada wiring layanan terkelola. Seluruh layanan menggunakan `ClusterIP`;
ingress **dinonaktifkan secara default**.

### 1. Membuat Cluster Lokal

```bash
# kind
kind create cluster --name cloudops

# k3d
k3d cluster create cloudops
```

### 2. Memuat Image ke Dalam Cluster

```bash
for t in api ml event-processor; do
  docker build --target "$t" -t "cloudops-$t:local" .
  kind load docker-image "cloudops-$t:local" --name cloudops   # kind
done
```

### 3. Membuat Namespace

```bash
kubectl apply -f infrastructure/kubernetes/namespaces/
```

### 4. Memvalidasi Chart

```bash
helm lint infrastructure/kubernetes/helm/cloudops-ai
helm template cloudops-ai infrastructure/kubernetes/helm/cloudops-ai
```

### 5. Deploy

```bash
helm upgrade --install cloudops-ai infrastructure/kubernetes/helm/cloudops-ai \
  --namespace cloudops-dev \
  --create-namespace
```

### 6. Menjalankan Migrasi

Image API membawa Alembic tetapi tidak menjalankan migrasi saat start:

```bash
kubectl exec -n cloudops-dev deploy/cloudops-ai-api -- alembic upgrade head
```

### 7. Mengakses Layanan

```bash
kubectl port-forward -n cloudops-dev svc/cloudops-ai-api 8000:8000
kubectl port-forward -n cloudops-monitoring svc/cloudops-prometheus 9090:9090
kubectl port-forward -n cloudops-monitoring svc/cloudops-grafana 3000:3000
```

### Override Per-Cluster

Atur StorageClass apabila default cluster Anda tidak sesuai:

```bash
helm upgrade --install cloudops-ai infrastructure/kubernetes/helm/cloudops-ai \
  --set postgres.storage.storageClass=standard
```

Aktifkan Ingress hanya jika cluster Anda menjalankan controller (misalnya `nginx` untuk
kind, `traefik` untuk k3d):

```bash
helm upgrade --install cloudops-ai infrastructure/kubernetes/helm/cloudops-ai \
  --set ingress.enabled=true --set ingress.className=nginx
```

---

## CI

Continuous integration berjalan pada setiap pull request dan push ke `main`
(`.github/workflows/ci.yml`):

- **Python Quality Gates & Security** — Ruff lint/format, Mypy, Pytest dengan
  coverage, PyPA `pip-audit`
- **Helm Chart & Manifest Validation** — `helm lint`, `helm template`, dan
  guard yang memastikan output hasil render tetap cloud-neutral
- **Local Docker Compose Validation** — `docker compose config`, guard yang
  memastikan tidak ada cloud SDK terpasang, kesehatan PostgreSQL, kesehatan API,
  dan job evaluasi ML
- **Container Build & Image Security Scan** — build Docker multi-target dengan
  cache buildx dan pemindaian kerentanan Trivy

CI tidak memerlukan kredensial cloud maupun akun registry. Tidak ada workflow
deployment otomatis: rilis dijalankan secara manual dari mesin lokal.

---

## Observabilitas

API mengekspos metrik Prometheus di `GET /metrics` dan mengembalikan header
`X-Request-ID` untuk korelasi log. Helm chart mencakup tumpukan ringan
Prometheus/Grafana beserta dashboard yang sudah diprovisioning. Lihat
[Observability & Monitoring](docs/architecture/observability.md) untuk metrik,
alert, dan instruksi validasi lokal.

---

## Dokumentasi Proyek

| Dokumen | Kegunaan |
|---|---|
| [AGENTS.md](AGENTS.md) | Aturan rekayasa, perintah, dan pengendalian cakupan |
| [docs/architecture/](docs/architecture/) | Pemrosesan event, Kubernetes, observabilitas, CI/CD |
| [docs/decisions/](docs/decisions/) | Architecture Decision Records (0003 dan 0004 digantikan oleh 0005) |
| [docs/evaluation/](docs/evaluation/) | Metodologi ML, hasil, keterbatasan, reproduksibilitas |

## Lisensi

MIT
