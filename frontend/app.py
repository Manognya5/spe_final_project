from flask import Flask, render_template, request
import requests
import os
import psycopg2
import json

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
        response = requests.get(BACKEND_URL+"/api/data")
        print(type(response))
        aqi_dumps = json.dumps(response)
        aqi_live_data = json.loads(aqi_dumps)
        
        response = "something"
    except Exception as e:
        message = f"Error: {e}"
        response = f"Error: {e}"
    return render_template('index.html', message=message, aqi_dumps=aqi_dumps, aqi_live_data=aqi_live_data, length=len(response))

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form['username']
        password = request.form['username']
        role = request.form.get('role')
        payload = {
            'username': username,
            'password': password, 
            'role': role
        }

        response = requests.post(BACKEND_URL+"/api/login", json=payload) # get 200 + user id or error and send that
    except Exception as e:
        print(f"Error {e}")
        message = f"{e}"
    return render_template('index.html', message=response)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
