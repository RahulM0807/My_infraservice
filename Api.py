from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # allows requests from React frontend

# --- Create database and table if not exists ---
def init_db():
    conn = sqlite3.connect("enquiries.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Route to save enquiry ---
@app.route("/api/enquiry", methods=["POST"])
def save_enquiry():
    try:
        data = request.get_json()
        name = data.get("name")
        phone = data.get("phone")
        email = data.get("email")
        message = data.get("message")

        # Simple validation
        if not name or not phone or not email:
            return jsonify({"error": "Missing required fields"}), 400

        conn = sqlite3.connect("enquiries.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO enquiries (name, phone, email, message, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, phone, email, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Enquiry saved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Route to view all enquiries (for admin use) ---
@app.route("/api/enquiries", methods=["GET"])
def get_enquiries():
    conn = sqlite3.connect("enquiries.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM enquiries ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    enquiries = [
        {
            "id": row[0],
            "name": row[1],
            "phone": row[2],
            "email": row[3],
            "message": row[4],
            "created_at": row[5],
        }
        for row in rows
    ]
    return jsonify(enquiries)


if __name__ == "__main__":
    app.run(debug=True)

