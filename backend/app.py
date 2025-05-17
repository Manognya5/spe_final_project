from flask import Flask, jsonify, request, session
import os
import psycopg2
import itertools
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'secret'

db_host = os.getenv("DB_HOST", "postgres-service") 
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")

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
        except Exception as e:
            print(f"Error connecting to database: {e}")
        if conn != -1:
            print("In this")
            cur = conn.cursor()
            cur.execute("SELECT * FROM aqi_data_24hr ORDER BY last_updated DESC LIMIT 60;") 
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            results = [dict(zip(colnames, row)) for row in rows]
            cur.close()
            conn.close()
            return jsonify(results)
        else:
            return jsonify({'error': "no conn"}), 500


    except Exception as e:
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
            except Exception as e:
                print(f"Error connecting to database: {e}")
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
                #print(row1)
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

                    else:
                        html_code = 404
                        msg += "invalid credentials"

                cur.close()
                conn.close()
                return jsonify({"status": html_code, "msg": msg, "user_id": user_id})
            else:
                return jsonify({"status": 500, "msg": "no conn", "user_id": user_id})


        except Exception as e:
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
            except Exception as e:
                print(f"Error connecting to database: {e}")
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

                    cur.execute("""
                        SELECT GREATEST(
                            NULLIF(PM10_avg, 'NA')::FLOAT,
                            NULLIF(PM2_avg, 'NA')::FLOAT,
                            NULLIF(NO2_avg, 'NA')::FLOAT,
                            NULLIF(NH3_avg, 'NA')::FLOAT,
                            NULLIF(SO2_avg, 'NA')::FLOAT,
                            NULLIF(CO_avg, 'NA')::FLOAT,
                            NULLIF(OZONE_avg, 'NA')::FLOAT
                        ) AS max_avg_pollutant
                        FROM aqi_data_24hr
                        WHERE station = %s
                        AND PM10_avg IS NOT NULL
                        AND PM2_avg IS NOT NULL
                        AND NO2_avg IS NOT NULL
                        AND NH3_avg IS NOT NULL
                        AND SO2_avg IS NOT NULL
                        AND CO_avg IS NOT NULL
                        AND OZONE_avg IS NOT NULL
                        ORDER BY last_updated DESC
                        LIMIT 1;
                        """, (permanent_location,))


                    result = cur.fetchone()
                    print(result)
                    output += generate_recommendation(result, permanent_location, repiratory_ailments)

                    print("genai op:" + output)

                cur.close()
                conn.close()
                return jsonify({"status": html_code, "msg": msg, "output": output})
            else:
                return jsonify({"status": 500, "msg": "no conn", "output": "Our genai model is taking too much time to load no conn"})


        except Exception as e:
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
        except Exception as e:
            print(f"Error connecting to database: {e}")
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
                msg += "Registered. Please login to continue"
                html_code = 200
            else:
                cur.execute("INSERT INTO admin_users (username, password) VALUES (%s, %s)", (username, input_password))
                conn.commit()
                print("entry made in admin db")
                msg += "Registered. Please login to continue"
                html_code = 200

            cur.close()
            conn.close()
            return jsonify({"status": html_code, "msg": msg})
        else:
            return jsonify({"status": 500, "msg": "no conn"})


    except Exception as e:
        return jsonify({"status": 500, "msg": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

