from flask import Flask, render_template, request, flash, redirect, url_for
import re
from dotenv import load_dotenv
import os
import requests

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-random-string"
load_dotenv()
PERSPECTIVE_API_KEY = os.getenv("PERSPECTIVE_API_KEY")

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

def check_spam_perspective(text):
    """Send text to Google Perspective API and return True if it seems spammy."""
    url = f"https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={PERSPECTIVE_API_KEY}"

    # What we send to Google
    data = {
        "comment": {"text": text},
        "languages": ["en"],
        "requestedAttributes": {"SPAM": {}, "TOXICITY": {}}
    }

    try:
        response = requests.post(url, json=data)
        result = response.json()
        spam_score = result["attributeScores"]["SPAM"]["summaryScore"]["value"]
        toxic_score = result["attributeScores"]["TOXICITY"]["summaryScore"]["value"]

        # You can tune this threshold:
        if spam_score > 0.7 or toxic_score > 0.7:
            return True  # looks spammy
        return False
    except Exception as e:
        print("Perspective API error:", e)
        return False

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

        # Validate each field separately
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

        # Otherwise process message
        flash("Message sent", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html", title="Contact", errors=errors, form=form_data)


if __name__ == "__main__":
    app.run()
