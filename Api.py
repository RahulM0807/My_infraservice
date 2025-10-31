from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# --- Database connection ---
DB_URL = "postgresql://myinfra_user:NToAqUPNtRrOB44ZFrL1Rd6kxJg4e7SY@dpg-d42e6sp5pdvs73d16sug-a/myinfra"

def get_db_connection():
    conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    return conn

# --- Create table if not exists ---
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# --- Save enquiry ---
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

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO enquiries (name, phone, email, message, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, phone, email, message, datetime.now()))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"success": True, "message": "Enquiry saved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Get all enquiries ---
@app.route("/api/enquiries", methods=["GET"])
def get_enquiries():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM enquiries ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
