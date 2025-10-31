from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Use environment variable for DB connection (Render provides DATABASE_URL)
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://myinfra_user:NToAqUPNtRrOB44ZFrL1Rd6kxJg4e7SY@dpg-d42e6sp5pdvs73d16sug-a/myinfra")

def get_connection():
    return psycopg.connect(DATABASE_URL)

@app.route("/api/enquiry", methods=["POST"])
def save_enquiry():
    try:
        data = request.get_json()
        name = data.get("name")
        phone = data.get("phone")
        email = data.get("email")
        message = data.get("message")

        if not name or not phone or not email:
            return jsonify({"error": "Missing required fields"}), 400

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS enquiries (
                        id SERIAL PRIMARY KEY,
                        name TEXT,
                        phone TEXT,
                        email TEXT,
                        message TEXT,
                        created_at TIMESTAMP
                    )
                """)
                cur.execute("""
                    INSERT INTO enquiries (name, phone, email, message, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, phone, email, message, datetime.now()))
            conn.commit()

        return jsonify({"success": True, "message": "Enquiry saved successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/enquiries", methods=["GET"])
def get_enquiries():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM enquiries ORDER BY created_at DESC")
                rows = cur.fetchall()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
