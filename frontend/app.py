from flask import Flask, render_template
import requests
import os

app = Flask(__name__)

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000/api/hello')


@app.route('/')
def index():
    try:
        response = requests.get(BACKEND_URL)
        message = response.json().get('message', 'No message from backend.')
    except Exception as e:
        message = f"Error: {e}"
    return render_template('index.html', message=message)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
