# main.py
import os
import secrets

# Generate random secret key
secret_key = secrets.token_hex(32)

# Set environment variable **before importing app**
os.environ["FLASK_SECRET_KEY"] = secret_key

# Now import app
from app import app

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
