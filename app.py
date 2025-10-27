from flask import Flask, render_template, request, flash, redirect, url_for
import re
from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

#  API Keys and Webhooks
PERSPECTIVE_API_KEY = os.getenv("PERSPECTIVE_API_KEY")
DISCORD_WEBHOOK_NORMAL = os.getenv("DISCORD_WEBHOOK_NORMAL")
DISCORD_WEBHOOK_SPAM = os.getenv("DISCORD_WEBHOOK_SPAM")
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

# Send to Discord
def send_to_discord(webhook_url, name, email, message, spam_score=None, toxic_score=None, is_spam=False):
    """Send message to Discord using embeds for better formatting."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    embed = {
        "title": "Contact Form Submission" if not is_spam else "Potential Spam Detected",
        "color": 0x5A827E if not is_spam else 0xBE5050,  # teal for normal, red for spam
        "fields": [
            {"name": "Name", "value": name or "N/A", "inline": False},
            {"name": "Email", "value": email or "N/A", "inline": False},
            {"name": "Message", "value": message or "N/A", "inline": False},
        ],
        "footer": {
            "text": f"Received at {timestamp} UTC"}}

    if spam_score is not None and toxic_score is not None:
        embed["fields"].append({
            "name": "Spam Analysis",
            "value": f"Spam Score: **{spam_score:.2f}** | Toxicity Score: **{toxic_score:.2f}**",
            "inline": False})

    payload = {
        "embeds": [embed]}

    try:
        requests.post(webhook_url, json=payload)
    except Exception as e:
        print("Discord webhook error:", e)

# Check spam with Perspective API
def check_spam_perspective(text):
    """Send text to Google Perspective API and return True if it seems spammy."""
    url = f"https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={PERSPECTIVE_API_KEY}"

    # What we send to Google
    data = {
        "comment": {"text": text},
        "languages": ["en"],
        "requestedAttributes": {"SPAM": {}, "TOXICITY": {}}}

    try:
        response = requests.post(url, json=data)
        result = response.json()
        spam_score = result["attributeScores"]["SPAM"]["summaryScore"]["value"]
        toxic_score = result["attributeScores"]["TOXICITY"]["summaryScore"]["value"]

        return spam_score, toxic_score

    except Exception as e:
        print("Perspective API error:", e)
        return 0.0, 0.0

@app.route("/")
def home():
    return render_template("home.html", title="Home")

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html', title='Portfolio')

@app.route("/contact", methods=["GET", "POST"])
def contact():
    errors = {}
    form_data = {"name": "", "email": "", "request": ""}

    if request.method == "POST":
        # Get and sanitize form data
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        message = (request.form.get("request") or "").strip()
        honeypot = (request.form.get("hp_name") or "").strip()

        # Keep the entered data so the form remembers it
        form_data = {"name": name, "email": email, "request": message}

        # Honeypot check
        if honeypot:
            flash("Spam detected.", "error")
            return render_template("contact.html", title="Contact", errors=errors, form=form_data)

        # Validate fields
        if not name:
            errors["name"] = "Please enter your name."
        if not email:
            errors["email"] = "Please enter your email."
        elif not EMAIL_RE.match(email):
            errors["email"] = "Please enter a valid email address."
        if not message:
            errors["request"] = "Please describe your request."

        # If any errors, re-render form with field-specific messages
        if errors:
            return render_template("contact.html", title="Contact", errors=errors, form=form_data)

        # Spam check
        spam_score, toxic_score = check_spam_perspective(message)
        is_spam = spam_score > 0.5 or toxic_score > 0.5

        if is_spam:
            send_to_discord(DISCORD_WEBHOOK_SPAM, name, email, message, spam_score, toxic_score, is_spam=True)
            flash("Your message was received but is under review.", "error")
        else:
            send_to_discord(DISCORD_WEBHOOK_NORMAL, name, email, message, is_spam=False)
            flash("Message sent", "success")

        return redirect(url_for("contact"))

    return render_template("contact.html", title="Contact", errors=errors, form=form_data)


#if __name__ == "__main__":
#    app.run()
