# FastAPI + PostgreSQL Deployment (GCP Ubuntu VM)

This guide describes deploying the app on Google Cloud Platform (GCP) using an Ubuntu 22.04 LTS VM.

---

## 1) Create the VM

- In GCP Console, create a Compute Engine VM (e2-medium recommended: 2 vCPU, 4 GB RAM).
- Ensure it has an External IP.
- SSH into the VM for the following steps.

---

## 2) System Update and Packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
  git curl wget unzip build-essential \
  python3 python3-pip python3-venv \
  postgresql postgresql-contrib
```

---

## 3) Initialize PostgreSQL

Switch to the postgres user and create the DB and user:
```bash
sudo -i -u postgres
psql
```

Run in psql:
```sql
CREATE DATABASE fastapi_db;
CREATE USER fastapi_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi_user;
\q
```

Exit back to your user:
```bash
exit
```

---

## 4) Optional: Remote PostgreSQL Access

Enable remote access only if you need to connect from outside the VM.

Edit `postgresql.conf`:
```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
```
Set:
```conf
listen_addresses = '*'
```

Edit `pg_hba.conf`:
```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```
Add:
```conf
host    all    all    0.0.0.0/0    scram-sha-256
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

Then open port `5432/tcp` in GCP VPC firewall (prefer restricting to trusted IPs).

---

## 5) Fetch the Application Source

Create a working directory and clone the repo:
```bash
cd ~
mkdir -p ~/app/src
cd ~/app/src
git clone https://github.com/lanyama19/fastapi-project.git .
```

---

## 6) Python Virtual Environment

Create and activate a venv, then install dependencies:
```bash
python3 -m venv ~/app/venv
source ~/app/venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

---

## 7) Environment Variables

Create an `.env` file in your home directory:
```bash
nano ~/.env
```

Example values:
```env
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432
DATABASE_NAME=fastapi_db
DATABASE_USER=fastapi_user
DATABASE_PASSWORD=yourpassword
SECRET_KEY=your_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Load them into the current shell (optional):
```bash
set -o allexport; source ~/.env; set +o allexport
```

---

## 8) Alembic Database Migrations

With the virtualenv active:
```bash
alembic upgrade head
```

Ensure Alembic points at your DB, e.g.:
```
postgresql+psycopg://fastapi_user:yourpassword@127.0.0.1:5432/fastapi_db
```

---

## 9) Run with Gunicorn + Uvicorn Workers

Quick test run:
```bash
gunicorn -w 3 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

Rule of thumb for workers: `2 * CPU cores + 1`.

---

## 10) Create a systemd Service

Create a service unit to run on boot:
```bash
sudo nano /etc/systemd/system/fastapi.service
```

Example content (adjust your username and paths):
```ini
[Unit]
Description=FastAPI Application
After=network.target

[Service]
User=<your-username>
Group=<your-username>
WorkingDirectory=/home/<your-username>/app/src
Environment="PATH=/home/<your-username>/app/venv/bin"
EnvironmentFile=/home/<your-username>/.env
ExecStart=/home/<your-username>/app/venv/bin/gunicorn -w 3 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi
systemctl status fastapi
```

---

## 11) GCP Firewall

If exposing port 8000 directly (or front with Nginx on 80/443), open the firewall rule:
```bash
gcloud compute firewall-rules create allow-fastapi-8000 \
  --allow=tcp:8000 \
  --source-ranges=0.0.0.0/0 \
  --network=default
```

Prefer locking this down to trusted IP ranges when possible.

---

## 12) Test the App

From the VM:
```bash
curl http://127.0.0.1:8000/
```

From outside:
```
http://<VM_EXTERNAL_IP>:8000/docs
```

