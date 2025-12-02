from flask import Flask, request, jsonify
import smtplib, ssl, os, logging
from email.message import EmailMessage
from dotenv import load_dotenv
from premailer import transform

load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM")
USE_STARTTLS = os.getenv("USE_STARTTLS", "false").lower() == "true"
APP_PORT = int(os.getenv("APP_PORT", "5000"))

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/send-email")
def send_email():
    # Expect multipart/form-data with "to" and "file" (HTML file)
    if "to" not in request.form or "file" not in request.files:
        return jsonify({"error": "Missing 'to' or 'file' in form-data"}), 400

    recipient = request.form["to"].strip()
    upload = request.files["file"]
    title = request.form["subject"].strip()

    if not recipient or upload.filename == "":
        return jsonify({"error": "Recipient or file missing"}), 400

    # Basic file-type check
    if not (upload.filename.lower().endswith(".html") or upload.filename.lower().endswith(".htm")):
        return jsonify({"error": "Only .html/.htm files are accepted"}), 415

    try:
        html_content = upload.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return jsonify({"error": f"Unable to read HTML: {e}"}), 400

    # Build email
    subject = title
    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content("Your email client does not support HTML. Please view this message in an HTML-capable client.")
    msg.add_alternative(html_content, subtype="html")
    html_content = transform(html_content)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            if USE_STARTTLS:
                server.starttls(context=context)
            if SMTP_USER:
                server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        app.logger.info("Email sent to %s via %s:%s", recipient, SMTP_HOST, SMTP_PORT)
        return jsonify({"status": "sent", "to": recipient})
    except Exception as e:
        app.logger.exception("Failed to send email")
        return jsonify({"error": str(e)}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT, debug=True)
