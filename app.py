from flask import Flask
from CodeFunctions import home

app = Flask(__name__)


@app.route("/")
def home_route():
    return home()

if __name__ == '__main__':
    app.run()
