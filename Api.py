from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Use Render's DATABASE_URL or local fallback
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://myinfra_user:NToAqUPNtRrOB44ZFrL1Rd6kxJg4e7SY@dpg-d42e6sp5pdvs73d16sug-a/myinfra"
)

def get_connection():
    return psycopg.connect(DATABASE_URL)

# ✅ Save Enquiry
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
                # Create table if it doesn't exist
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

                # Insert record
                cur.execute("""
                    INSERT INTO enquiries (name, phone, email, message, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, phone, email, message, datetime.now()))

        return jsonify({"success": True, "message": "✅ Enquiry saved successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Get All Enquiries
@app.route("/api/enquiries", methods=["GET"])
def get_enquiries():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, phone, email, message, created_at
                    FROM enquiries
                    ORDER BY created_at DESC
                """)
                rows = cur.fetchall()

        # Convert tuples → list of dicts
        enquiries = [
            {
                "id": r[0],
                "name": r[1],
                "phone": r[2],
                "email": r[3],
                "message": r[4],
                "created_at": r[5].strftime("%Y-%m-%d %H:%M:%S") if r[5] else None,
            }
            for r in rows
        ]

        return jsonify(enquiries)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ✅ 2️⃣ Save Cost Estimator data
@app.route("/api/save_estimate", methods=["POST"])
def save_estimate():
    try:
        data = request.get_json()
        name = data.get("name")
        phone = data.get("phone")
        plot_size = data.get("plotSize")
        floors = data.get("floors")
        location = data.get("location")
        built_up_area = data.get("builtUpArea")

        if not name or not phone:
            return jsonify({"error": "Name and Phone are required"}), 400

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS estimates (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        plot_size TEXT,
                        floors TEXT,
                        location TEXT,
                        built_up_area INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cur.execute("""
                    INSERT INTO estimates (name, phone, plot_size, floors, location, built_up_area, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (name, phone, plot_size, floors, location, built_up_area, datetime.now()))

        return jsonify({"success": True, "message": "✅ Estimate saved successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ 3️⃣ Get all saved estimates
@app.route("/api/estimates", methods=["GET"])
def get_estimates():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, phone, plot_size, floors, location, built_up_area, created_at
                    FROM estimates
                    ORDER BY created_at DESC
                """)
                rows = cur.fetchall()

        estimates = [
            {
                "id": r[0],
                "name": r[1],
                "phone": r[2],
                "plot_size": r[3],
                "floors": r[4],
                "location": r[5],
                "built_up_area": r[6],
                "created_at": r[7].strftime("%Y-%m-%d %H:%M:%S") if r[7] else None,
            }
            for r in rows
        ]

        return jsonify(estimates)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
