# Rencana Deployment — Inventory API (Track B: Containers)

Region `us-east-1`, lingkungan AWS Academy Lab "Building Microservices and a CI/CD Pipeline with AWS".

## Layanan

| Service | Status | Port host → container | Fungsi |
|---|---|---|---|
| `inventory-service` | **Dibangun minggu 12** | 8080 → 5000 | CRUD data barang (`/items`) |
| `stock-service` | Direncanakan | 8081 → 5000 | Mencatat barang masuk/keluar, memanggil `inventory-service` untuk update stok |

## Tahap 1 — Week 12 (setup awal, selesai)

1. Buka EC2 `MonolithicAppServer` bawaan lab lewat **EC2 Instance Connect**.
2. Clone repo dan build image:
   ```bash
   git clone https://github.com/<user>/<repo>.git
   cd <repo>/inventory-service
   docker build -t inventory-service:v1 .
   ```
3. Buat repository ECR privat dan push image:
   ```bash
   ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
   REGISTRY=$ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
   aws ecr create-repository --repository-name inventory-service --region us-east-1
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $REGISTRY
   docker tag inventory-service:v1 $REGISTRY/inventory-service:v1
   docker push $REGISTRY/inventory-service:v1
   ```
   Kredensial sesi AWS Academy (sementara) dipakai hanya untuk langkah ini lalu dihapus dari server (`rm ~/.aws/credentials`, `docker logout`).
4. Jalankan container dari image ECR dengan volume bernama agar data SQLite tetap ada saat restart:
   ```bash
   docker run -d --name inventory-service --restart unless-stopped \
     -p 8080:5000 -v inventory-data:/data $REGISTRY/inventory-service:v1
   ```
5. Uji konektivitas dan CRUD: `./scripts/crud-test.sh http://localhost:8080`.

## Tahap 2 — minggu berikutnya

- Bangun `stock-service` (image kedua di ECR, `stock-service:v1`), komunikasi lewat jaringan Docker bersama (`docker network create inventory-net`).
- Pindah ke **Amazon ECS (Fargate)** + Application Load Balancer, satu target group per service (`/items*` → inventory, `/stock*` → stock).
- Ganti SQLite ke database terkelola (RDS) agar data tidak terikat satu instance.
- Otomatisasi build & deploy dengan CodePipeline/CodeBuild (CI/CD), image di-tag per commit.

## Keamanan

- Repository ECR privat, scan on push aktif, enkripsi AES-256 at rest.
- Tidak ada access key di kode/repo; kredensial lab hanya sementara di server.
- Container berjalan sebagai user non-root (`USER app` di Dockerfile).
- Security group lab hanya membuka port 22 dan 80; API diuji dari dalam instance (port 8080 tidak dibuka ke publik).
