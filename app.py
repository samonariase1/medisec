"""
Root level app entry point.

A rooot level .py is required by vercel naned as an app.py or index.py file
"""

from backend.app import create_app


app = create_app()
