from flask import Flask, render_template
import requests
import os
import psycopg2

app = Flask(__name__)

BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:5000')
db_host = os.getenv("DB_HOST", "postgres-service") 
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")

# Connect to PostgreSQL
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


@app.route('/')
def index():
    message = ""
    response = ""
    try:
        response = requests.get(BACKEND_URL+"/api/hello")
        print("hello done")
        message = response.json().get('message', 'No message from backend.')
        # response = requests.get(BACKEND_URL+"/api/data")
        response = "something"
    except Exception as e:
        message = f"Error: {e}"
        response = f"Error: {e}"
    return render_template('index.html', message=message, response=response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
