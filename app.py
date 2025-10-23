from flask import Flask, render_template, request, flash, redirect, url_for
import re

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-random-string"

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

@app.route("/")
def home():
    return render_template("home.html", title="Home")

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html', title='Portfolio')

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        message = (request.form.get("request") or "").strip()
        honeypot = (request.form.get("hp_name") or "").strip()

        errors = []

        # Honeypot check: if filled, assume bot and reject
        if honeypot:
            errors.append("Spam detected.")

        # Required fields (server-side)
        if not name:
            errors.append("Please enter your name.")
        if not email:
            errors.append("Please enter your email.")
        if not message:
            errors.append("Please describe your request.")

        # Email format check
        if email and not EMAIL_RE.match(email):
            errors.append("Please enter a valid email address.")

        if errors:
            for e in errors:
                flash(e, "error")
            # Return the form page
            return render_template("contact.html", title="Contact")
        else:
            # At this point the data passed basic checks.
            # Placeholder: here you would send email or save to DB.
            flash("Message sent", "success")
            return redirect(url_for("contact"))

    # GET
    return render_template("contact.html", title="Contact")

if __name__ == "__main__":
    app.run()
