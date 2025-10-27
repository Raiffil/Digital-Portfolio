#!/usr/bin/env bash

# Make sure the environment is production
export FLASK_ENV=production

# Run Gunicorn with your Flask app
# --bind: listens on all interfaces on the port Azure assigns
# --workers: number of worker processes (adjust based on your app size)
# --timeout: seconds before a worker is killed if unresponsive
gunicorn --bind=0.0.0.0:$PORT --workers=4 --timeout 600 app:app
