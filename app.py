from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html", title="Home")

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html', title='Portfolio')

@app.route("/contact")
def contact():
    return render_template("contact.html", title="Contact")

if __name__ == "__main__":
    app.run()
