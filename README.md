
# Cyber Report Email Service 

This is a container that shows how to send an HTML file to an inbox using a Python Flask service over SMTP.

How it runs:

- Docker + MailHog (captures emails locally; nothing gets sent to the outside world).
---

## What you need to have installed

1. Install **Docker Desktop** (Windows/Mac/Linux)
2. Install **Postman** to test the endpoint

---

## Running with Docker 

1) Open a terminal in this folder and run:

	docker compose up --build

This starts two containers:
- `email_service` at **http://localhost:5000**
- `mailhog` (fake SMTP server) with web UI at **http://localhost:8025**

2) Test the API with Postman:
- Import the `postman_collection.json` file into Postman.
- Open **Send Email** request.
- Set **Body** → **form-data**:
  - Key: `to` (text) → value: `anyone@example.com` (MailHog doesn't care)
  - Key: `file` (file) → choose `sample_report.html` from this folder
- Click **Send**.

3) View the email:
- Open **http://localhost:8025** in your browser.
- You should see the email appear in MailHog's inbox.

---

## Expected API responses

- **Success (200):**
```json
{ "status": "sent", "to": "test@example.com" }
```

- **Common errors:**
  - `400 Missing 'to' or 'file'` → You didn’t include form-data fields correctly.
  - `415 Only .html/.htm` → You uploaded a non-HTML file.
  - `502` → SMTP connection/login failed (wrong host/port/creds, or blocked by firewall).

---

## Files in this pack

- `email_service.py` — Flask app exposing `POST /send-email` and `GET /health`
- `requirements.txt` — Python dependencies
- `.env.example` — Sample environment variables
- `sample_report.html` — Mock HTML to send
- `Dockerfile` — Container build for the service
- `docker-compose.yml` — Runs the service + MailHog
- `postman_collection.json` — One-click request you can import into Postman

---


