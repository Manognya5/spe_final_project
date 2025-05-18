from flask import Flask, jsonify, request, session
import os
import psycopg2
import itertools
import google.generativeai as genai
import json
import logging


app = Flask(__name__)
app.secret_key = 'secret'

db_host = os.getenv("DB_HOST", "postgres-service") 
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")

def setup_logger():
    log_dir = '/var/log/app'
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger('backend')
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    logger.handlers = []
    
    # File handler for JSON logs
    file_handler = logging.FileHandler(f'{log_dir}/backend.log', mode='a')
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # JSON formatter
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
                "service": "backend",
                "level": record.levelname.lower(),
                "message": record.getMessage()
            }
            return json.dumps(log_record)
    
    formatter = JSONFormatter()
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Test the logger
    logger.info("Logger configured successfully")
    return logger

logger = setup_logger()

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

def generate_recommendation(aqi, location, respiratory_ailments):
    genai.configure(api_key="AIzaSyA_a9dk5E0LvqTsDl8n5qmGjOckX4p8T4M")

    model = genai.GenerativeModel("gemini-2.0-flash")
    content = f"I stay in {location}, I have {respiratory_ailments} and taccording to the current AQI, can you generate some precautions to take and any emergency hospitals if required?"

    response = model.generate_content(content)

    print(response.text)
    return response.text

@app.route('/api/hello')
def hello():
    return jsonify(message="Hello from the backend!")

@app.route('/api/data')
def fetch_data():
    try:
        conn = -1
        try:
            conn = psycopg2.connect(
                host=db_host,
                dbname=db_name,
                user=db_user,
                password=db_password
            )
            print("Connected to the database successfully!")
            logger.info("Connected to the database successfully!")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            logger.error(f"Error connecting to database: {e}")

        if conn != -1:
            print("In this")
            cur = conn.cursor()
            cur.execute("SELECT * FROM aqi_data_24hr ORDER BY last_updated DESC LIMIT 120;") 
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            results = [dict(zip(colnames, row)) for row in rows]
            cur.close()
            conn.close()
            return jsonify(results)
        else:
            return jsonify({'error': "no conn"}), 500


    except Exception as e:
        logger.error(f"error in /api/data: {str(e)}")
        return jsonify({'error in exception': str(e)}), 500

@app.route('/api/login', methods=["POST"])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        input_password = data['password']
        role = data['role']
        html_code = 500
        msg = ""
        try:
            conn = -1
            try:
                conn = psycopg2.connect(
                    host=db_host,
                    dbname=db_name,
                    user=db_user,
                    password=db_password
                )
                print("Connected to the database successfully!")
                logger.info("Connected to the database successfully!")
            except Exception as e:
                print(f"Error connecting to database: {e}")
                logger.error(f"Error connecting to database: {e}")
            if conn != -1:
                print("In this")
                cur = conn.cursor()
                if role == 'user':
                    cur.execute("SELECT password, id from users WHERE username = %s", (username,))
                else:
                    cur.execute("SELECT password, id from admin_users WHERE username = %s", (username,))

                row = cur.fetchall()
                row1 = list(itertools.chain(*row)) 
                msg += f"{row1}"
                #Check if passwords are equal
                logger.debug(f"fetching user details : {msg}")
                user_id = -1
                if len(row1) == 0:
                    html_code = 404
                    msg += "no user found"
                else:
                    msg += f"input pswqd: {input_password}, db_pswd: {row1[0]}"

                    if len(row1[0]) == 0:
                        html_code = 404
                        msg += "no user found"
                    elif row1[0] == input_password: #check if both encrypted ones are same
                        session['id'] = row1[1]
                        html_code = 200
                        msg += "login successful"
                        msg += f"input pswqd: {input_password}, db_pswd: {row1[0]}"
                        user_id = row1[1]
                        logger.info(f"{row1[1]} logged in")

                    else:
                        html_code = 404
                        msg += "invalid credentials"
                        logger.warning(f"{row1[1]} entered incorrect password")

                cur.close()
                conn.close()
                return jsonify({"status": html_code, "msg": msg, "user_id": user_id})
            else:
                return jsonify({"status": 500, "msg": "no conn", "user_id": user_id})


        except Exception as e:
            logger.error(f"Exception in /api/login : {str(e)}")
            return jsonify({"status": 500, "msg": str(e)})
        
@app.route('/api/recommendation', methods=["POST"])
def recommend():
    if request.method == 'POST':
        data = request.get_json()
        id = data['id']

        html_code = 500
        msg = ""
        output = ""
        try:
            conn = -1
            try:
                conn = psycopg2.connect(
                    host=db_host,
                    dbname=db_name,
                    user=db_user,
                    password=db_password
                )
                print("Connected to the database successfully!")
                logger.info("Connected to the database successfully!")
            except Exception as e:
                print(f"Error connecting to database: {e}")
                logger.error(f"Error connecting to database in recommendation: {e}")
            if conn != -1:
                print("In this")
                cur = conn.cursor()
            
                cur.execute("SELECT permanent_location, respiratory_ailments from users WHERE id = %s", (id,))
                

                row = cur.fetchall()
                row1 = list(itertools.chain(*row)) 
                msg += f"{row1}"


                if len(row1) == 0:
                    html_code = 404
                    msg += "no user found"
                else:
                    repiratory_ailments = row1[1]
                    permanent_location = row1[0]

                    result = ""
                    output += generate_recommendation(result, permanent_location, repiratory_ailments)
                    logger.info("Generated genai output")
                    print("genai op:" + output)

                cur.close()
                conn.close()
                return jsonify({"status": html_code, "msg": msg, "output": output})
            else:
                logger.error("Genai model didn't work as expected")
                return jsonify({"status": 500, "msg": "no conn", "output": "Our genai model is taking too much time to load no conn"})


        except Exception as e:
            logger.error(f"Genai model didn't work as expected: {str(e)}")
            return jsonify({"status": 500, "msg": str(e), "output": f"Our genai model is taking too much time to load {str(e)}"})
    
@app.route('/api/register' , methods=["GET", "POST"])
def register():
    
    html_code = 500
    msg = ""
    try:

        conn = -1
        try:
            conn = psycopg2.connect(
                host=db_host,
                dbname=db_name,
                user=db_user,
                password=db_password
            )
            print("Connected to the database successfully!")
            logger.info("Connected to the database successfully!")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            logger.error(f"Error connecting to database in register: {e}")
        if conn != -1:
            data = request.get_json()
            username = data['username']
            input_password = data['password']
            print(f"password din register {input_password}")
            role = data['role']
            cur = conn.cursor()
            if role == 'user':
                respiratory_ailments = data['respiratory_ailments'] ,
                phone_number = data['phone_number'],
                permanent_location = data['permanent_location']
                cur.execute("INSERT INTO users (username, password, respiratory_ailments, phone_number, permanent_location) VALUES (%s, %s, %s, %s, %s)", (username, input_password, respiratory_ailments, phone_number, permanent_location))
                conn.commit()
                print("entry made in db")
                logger.info(f"New user: {username} registered")
                msg += "Registered. Please login to continue"
                html_code = 200
            else:
                cur.execute("INSERT INTO admin_users (username, password) VALUES (%s, %s)", (username, input_password))
                conn.commit()
                print("entry made in admin db")
                msg += "Registered. Please login to continue"
                logger.info(f"New admin: {username} registered")
                html_code = 200

            cur.close()
            conn.close()
            return jsonify({"status": html_code, "msg": msg})
        else:
            logger.error("No connection to db in register")
            return jsonify({"status": 500, "msg": "no conn"})


    except Exception as e:
        logger.error(f"Error in register: {str(e)}")
        return jsonify({"status": 500, "msg": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

