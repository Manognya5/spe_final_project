from flask import Flask, render_template, request, session, redirect
import requests
import os
import psycopg2
import json
import logging

app = Flask(__name__)
app.secret_key = 'secret'


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:5000')

def encrypt_password(password, shift=3):
    encrypted = ""
    for char in password:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            encrypted += chr((ord(char) - base + shift) % 26 + base)
        elif char.isdigit():
            encrypted += chr((ord(char) - ord('0') + shift) % 10 + ord('0'))
        else:
            encrypted += char  # Leave special characters unchanged
    return encrypted

@app.route('/')
def index():
    message = ""
    response = ""
    aqi_dumps = {}

    try:
        response = requests.get(BACKEND_URL + "/api/data")
        logger.info("Received response of type: %s", type(response))
        logger.info("Response: %s", response)
        if (response.status_code == 200 or response.status_code == 201):
            aqi_dumps = json.dumps(response.json())
            logger.info("aqi dumps: %s", aqi_dumps)

        
    except Exception as e:
        logger.error("Exception in index: %s", e)
        message = f"Error: {e}"
        response = f"Error: {e}"
    logger.info("Before rendering")
    return render_template('index.html', message=message, aqi_dumps=aqi_dumps)

@app.route('/login', methods=['GET', 'POST'])
def login():
    aqi_dumps = {}
    if request.method == "GET":
        return render_template("login.html")
    else:
        try:
            response = requests.get(BACKEND_URL + "/api/data")
            logger.info("Received response of type: %s %s", type(response), response.json())
            logger.info("Response: %s", response)
            if (response.status_code == 200 or response.status_code == 201):
                aqi_dumps = json.dumps(response.json())
            logger.info("aqi dumps in login: %s", aqi_dumps)
            username = request.form['username']
            password = request.form['password']
            role = request.form.get('role')
            payload = {
                'username': username,
                'password': encrypt_password(password), 
                'role': role
            }
            logger.info("encry pswd %s", encrypt_password(password))
            response = requests.post(BACKEND_URL + "/api/login", json=payload)
            logger.info("Login response: %s", response.json())
            if response.json()['status'] != 200:
                return render_template("index.html", message=response.json()['msg'], aqi_dumps=aqi_dumps)
            else:
                session['id'] = response.json()['user_id']
                session['valid'] = 1
        except Exception as e:
            logger.error("Error in login: %s", e)
            response = f"{e}"
        return render_template('user_home.html', message=response, aqi_dumps=aqi_dumps)
    
@app.route('/recommend', methods=['GET'])
def recommend():
    logger.info(f"session: {session.get('valid','')}")
    payload = {
                'id': session.get('id',-1),
            }
    
    if session['valid'] == 1:
        response = requests.post(BACKEND_URL + "/api/recommendation", json=payload)
        response = response.json()

        logging.info(f"{response['status']} entooo {response['msg']}")
        return render_template("recommendation.html", message=response['output'])
    else:
        return redirect("/")

@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'GET':
        return render_template("register.html")
    else:
        aqi_dumps = {}
        response = requests.get(BACKEND_URL + "/api/data")
        logger.info("Received response of type: %s", type(response))
        logger.info("Response: %s", response)
        if (response.status_code == 200 or response.status_code == 201):
            aqi_dumps = json.dumps(response.json())
            logger.info("aqi dumps: %s", aqi_dumps)
        try:
            username = request.form['username']
            password = request.form['password']
            role = request.form.get('role')
            payload = {
                'username': username,
                'password': encrypt_password(password), 
                'role': role
            }
            if role == 'user':
                respiratory_ailments = request.form.get('respiratory_ailments', '')
                phone_number = request.form.get('phone_number', '')
                permanent_location = request.form.get('permanent_location', '')
                payload.update({
                    'respiratory_ailments': respiratory_ailments,
                    'phone_number': phone_number,
                    'permanent_location': permanent_location
                })

            response = requests.post(BACKEND_URL + "/api/register", json=payload)
            logger.info("Register response: %s", response.json())
        except Exception as e:
            logger.error("Error in register: %s", e)
            response = f"{e}"
        return render_template('index.html', message=response, aqi_dumps = aqi_dumps)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
