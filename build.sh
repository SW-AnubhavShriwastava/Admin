#!/bin/bash
pip install -r requirements.txt  # Install dependencies
gunicorn --bind 0.0.0.0:8000 wsgi:app  # Start the app using gunicorn
