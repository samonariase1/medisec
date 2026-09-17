"""
Root level app entry point.

A rooot level .py is required by vercel naned as an app.py or index.py file.

With this current implementation, app can be started by:
python3 app.py   OR
python3 backend/app.py
"""

from backend.app import create_app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
