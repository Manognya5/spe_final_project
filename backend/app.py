from flask import Flask, jsonify, request, session
import os
import psycopg2
import itertools

app = Flask(__name__)

db_host = os.getenv("DB_HOST", "postgres-service") 
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")


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
            cur.execute("SELECT * FROM aqi_data_24hr;") 
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

@app.route('/api/login')
def fetch_data():
    data = request.get_json()
    username = data['username']
    input_password = data['password']
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
            # cur.execute("SELECT * FROM user;") 
            cur.execute("SELECT password, id from user WHERE username = %s", (username,))
            row = cur.fetchall()
            row1 = list(itertools.chain(*row))      #Convert list of tuple to list
            #Check if passwords are equal
            #print(row1)
            if len(row1) == 0:
                html_code = 404
                msg += "no user found"
            else:
                if row1[0] == input_password:
                    session['id'] = row1[1]
                    html_code = 200
                    msg += "login successful"

                else:
                    html_code = 404
                    msg += "invalid credentials"

            cur.close()
            conn.close()
            return jsonify({"status": html_code, "msg": msg})
        else:
            return jsonify({"status": 500, "msg": "no conn"})


    except Exception as e:
        return jsonify({"status": 500, "msg": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

