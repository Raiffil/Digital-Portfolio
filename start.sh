#!/usr/bin/env bash

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=production

# Start the app using Gunicorn and bind to the port provided by Azure
# app:app -> first 'app' is your filename (app.py), second 'app' is your Flask instance
gunicorn --workers 4 --bind 0.0.0.0:$PORT app:app
