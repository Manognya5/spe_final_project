from flask import Flask, jsonify
import os
import psycopg2

app = Flask(__name__)

db_host = os.getenv("DB_HOST", "postgres-service") 
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
conn = -1
try:
    conn = psycopg2.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=db_password
    )
    print("Connected to the database successfully!")
except Exception as e:
    print(f"Error connecting to database: {e}")

@app.route('/api/hello')
def hello():
    return jsonify(message="Hello from the backend!")

@app.route('/api/data')
def fetch_data():
    try:
        if conn != -1:
            print("In this")
            cur = conn.cursor()
            cur.execute("SELECT * FROM aqi_data_24hr;") 
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            results = [dict(zip(colnames, row)) for row in rows]
            cur.close()
            
            return jsonify(results)
        else:
            return jsonify({'error': "no conn"}), 500

    except Exception as e:
        return jsonify({'error in exception': str(e)}), 500
conn.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
