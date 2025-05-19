from flask import Flask, render_template, request, session, redirect
import requests
import os
import psycopg2
import json
import logging

app = Flask(__name__, static_folder='static')
app.secret_key = 'secret'



def setup_logger():
    log_dir = '/var/log/app'
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger('frontend')
    logger.setLevel(logging.INFO)
    logger.handlers = []

    file_handler = logging.FileHandler(f'{log_dir}/frontend.log', mode='a')
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Standard fields we want in every log line
    STANDARD_FIELDS = ["user_id", "request_type", "action", "status"]

    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
                "service": "frontend",
                "level": record.levelname.lower(),
                "message": record.getMessage()
            }

            # Ensure all standard fields are present
            for field in STANDARD_FIELDS:
                log_record[field] = getattr(record, field, "")

            return json.dumps(log_record)

    formatter = JSONFormatter()
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logger configured successfully", extra={"action": "init", "user_id": "", "request_type":"", "status": "" })
    return logger


logger = setup_logger()

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s %(levelname)s %(message)s',
#     handlers=[
#         logging.FileHandler("app.log"),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:5000')
MODEL_URL = os.getenv('MODEL_URL', 'http://model:5005')

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
        logger.info("Received response of type: %s", type(response), extra={"action": "home", "user_id": "", "request_type":"get", "status": f"{response.status_code}" })
        # logger.info("Response: %s", response)
        if (response.status_code == 200 or response.status_code == 201):
            aqi_dumps = json.dumps(response.json())
            logger.info(f"aqi dumps size: {len(aqi_dumps)}")

        
    except Exception as e:
        logger.error("Exception in index: %s", e, extra={"action": "home", "user_id": "", "request_type":"", "status": f""})
        message = f"Error: {e}"
        response = f"Error: {e}"
    logger.info("rendering home")
    return render_template('index.html', message=message, aqi_dumps=aqi_dumps)

@app.route('/login', methods=['GET', 'POST'])
def login():
    aqi_dumps = {}
    if request.method == "GET":
        logger.info("rendered login", extra={"action": "login", "user_id": "", "request_type":"get", "status": f"200"})
        return render_template("login.html")
    else:
        try:
            response = requests.get(BACKEND_URL + "/api/data")
            logger.info("Received response of type: %s %s", type(response), response.json(), extra={"action": "login", "user_id": "", "request_type":"post", "status": f"{response.status_code}"})
            logger.info("Response: %s", response)
            if (response.status_code == 200 or response.status_code == 201):
                aqi_dumps = json.dumps(response.json())
            logger.info(f"aqi dumps in login size: {len(aqi_dumps)}")
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
                return redirect("/home")
            else:
                session['id'] = response.json()['user_id']
                session['valid'] = 1
        except Exception as e:
            logger.error("Error in login: %s", e, extra={"action": "login", "user_id": "", "request_type":"post", "status": f""})
            response = f"{e}"
        return render_template('user_home.html', message=response, aqi_dumps=aqi_dumps)
    
# after login
@app.route('/home', methods=["GET"])
def after_login():
    message = ""
    response = ""
    aqi_dumps = {}

    try:
        response = requests.get(BACKEND_URL + "/api/data")
        logger.info("Received response of type: %s", type(response), extra={"action": "user_home", "user_id": f"{session.get('id','')}", "request_type":"get", "status": f"{response.status_code}"})
        # logger.info("Response: %s", response)
        if (response.status_code == 200 or response.status_code == 201):
            aqi_dumps = json.dumps(response.json())
            logger.info(f"aqi dumps size: {len(aqi_dumps)}")

        
    except Exception as e:
        logger.error("Exception in index: %s", e, extra={"action": "user_home", "user_id": f"{session.get('id','')}", "request_type":"get", "status": f""})
        message = f"Error: {e}"
        response = f"Error: {e}"
    logger.info("rendering home")
    return render_template('user_home.html', message=message, aqi_dumps=aqi_dumps)

    
@app.route('/recommend', methods=['GET'])
def recommend():
    logger.info(f"session: {session.get('valid','')}")
    payload = {
                'id': session.get('id',-1),
            }
    
    if session['valid'] == 1:
        response = requests.post(BACKEND_URL + "/api/recommendation", json=payload)
        response = response.json()

        logging.info(f"{response['status']} recommend {response['msg']}", extra={"action": "home", "user_id": f"{session.get('id','')}", "request_type":"post", "status": f"{response['status']}"})
        return render_template("recommendation.html", message=response['output'])
    else:
        return redirect("/")

# @app.route('/predict', methods=['GET', 'POST'])
# def predict():
#     logger.info(f"session: {session.get('valid','')}")
#     payload = {
#                 'id': session.get('id',-1),
#             }
    
#     if session['valid'] == 1:
#         if request.method == 'GET':
#             return render_template("predict.html")
#         else:
#             city = request.form['city']
#             date = request.form['date']
#             payload.update({
#                 "city": city,
#                 "date": date
#             })
#             response = requests.post(MODEL_URL + "/predict", json=payload)
#             response = response.json()
#             logging.info(f"Full response JSON: {response}")

#                 # Use .get() with default values to avoid KeyError
#             status = response.get('status', 'No status')
#             msg = response.get('msg', 'No msg')
#             predicted = response.get('predicted_aqi_next_7_days', [])
#             output = response.get('output', 'No output key in response')
#             logging.info(f"{status} recommend {msg} formatted data {predicted}")

#             #logging.info(f"{response['status']} recommend {response['msg']} formatted data {response['predicted_aqi_next_7_days']}")
#             return render_template("predicted.html", message=response['output'], predicted=response['predicted_aqi_next_7_days'])
#     else:
#         return redirect("/")

# @app.route('/predict', methods=['GET', 'POST'])
# def predict():
#     # ... your code ...
#     logger.info(f"session: {session.get('valid','')}")
#     payload = {
#                 'id': session.get('id',-1),
#             }
    
#     if session['valid'] == 1:
#         if request.method == 'GET':
#             return render_template("predict.html")
#         else:
#             city = request.form['city']
#             date = request.form['date']
#             payload.update({
#                 "city": city,
#                 "date": date
#             })
#     response = requests.post(MODEL_URL + "/predict", json=payload)
#     response_json = response.json()

#     # Instead of accessing specific keys, just send whole JSON to template
#     return render_template("predicted.html", raw_json=response_json)

# @app.route('/predict', methods=['GET', 'POST'])
# def predict():
#     if session.get('valid') != 1:
#         return jsonify({"error": "Unauthorized"}), 401

#     if request.method == 'POST':
#         data = request.get_json()
#         city = data.get('city')
#         date = data.get('date')

#         payload = {
#             "id": session.get('id', -1),
#             "city": city,
#             "date": date
#         }

#         response = requests.post(MODEL_URL + "/predict", json=payload)
#         return jsonify(response.json())

#     return render_template("predicted.html")
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    logger.info(f"session: {session.get('valid', '')}")

    if session.get('valid') != 1:
        return redirect('/login')  # or render a 401 page

    if request.method == 'GET':
        return render_template("predict.html")
    else:
        try:
            city = request.form.get('city')
            date = request.form.get('date')

            payload = {
                "id": session.get('id', -1),
                "city": city,
                "date": date
            }

            response = requests.post(MODEL_URL + "/predict", json=payload)

            response.raise_for_status()  # raises exception for HTTP error
            response_json = json.dumps(response.json())
            logger.info(f"Full response JSON: {response_json}")
        

            return render_template("predicted.html",predicted=response_json, city=city, date=date)
        except Exception as e:
            logger.exception("Error during prediction")
            return render_template("predicted.html", error="Something went wrong. Please try again."), 500


@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'GET':
        logger.info("rendered register", extra={"action": "register", "user_id": "", "request_type":"get", "status": f"200"})
        return render_template("register.html")
    else:
        aqi_dumps = {}
        response = requests.get(BACKEND_URL + "/api/data")
        logger.info("Received response of type: %s", type(response))
        logger.info("Response: %s", response)
        if (response.status_code == 200 or response.status_code == 201):
            aqi_dumps = json.dumps(response.json())
            logger.info(f"aqi dumps len in register: {len(aqi_dumps)}")
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
            logger.info("Register response: %s", response.json(), extra={"action": "register", "user_id": "", "request_type":"post", "status": f""})
        except Exception as e:
            logger.error("Error in register: %s", e)
            response = f"{e}"
        return render_template('index.html', message=response, aqi_dumps = aqi_dumps)
@app.route("/logout")
def logout():
    session['valid'] = 0
    session['id'] = 0
    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
