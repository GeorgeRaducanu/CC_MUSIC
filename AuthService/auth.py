from flask import Flask, request, jsonify, render_template, redirect, url_for
import jwt
import datetime
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import requests
from prometheus_flask_exporter import PrometheusMetrics
import logging
import os
logging.basicConfig(level=logging.INFO)

IO_SERVICE_URL = 'http://io-service:5001'
AUTH_SERVICE_URL = 'http://auth-service:5000'
BUSINESS_LOGIC_URL = "http://business-logic:5002"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cheia_mea_ultra_secreta_si_smechera'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def generate_token(user_id, role):
    token = jwt.encode({
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def token_required(allowed_roles=[]):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'message': 'Token is missing!'}), 403
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                if data['role'] not in allowed_roles:
                    return jsonify({'message': 'Permission denied!'}), 403
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token has expired!'}), 403
            except Exception as e:
                return jsonify({'message': 'Token is invalid!'}), 403
        return decorated
    return decorator

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    data = request.form

    if request.method == 'POST':

        if not data['username'] or not data['password']:
            return jsonify({'message': 'Missing credentials'}), 400
        
        response = requests.post(f"{IO_SERVICE_URL}/insert_user", json={
            'username': data['username'],
            'password': data['password'],
            'role': 'admin'
        })
        logging.info("Am trecut de IO_SERVICE_URL")
        if response.status_code == 200:
            user_data = response.json()
            # token = generate_token(user_id=user_data['id'], role=user_data['role'])
            # redirect to login on the same page
            logging.info("Redirectez la login")
            return redirect(f"/auth/login")
    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    data = request.form
    if request.method == 'POST':
        user = data['username']
        password = data['password']
        if not user or not password:
            return jsonify({'message': 'Missing credentials'}), 400
    
        response = requests.post(f"{IO_SERVICE_URL}/get_user", json={'username': user, 'password': password})
        logging.info("Am trecut de IO_SERVICE_URL")
        if response.status_code == 200:
            user_data = response.json()
            token = generate_token(user_id=user_data['id'], role=user_data['role'])
            logging.info("You logged in successfully")

            return redirect(f"/business/?token={token}")
        elif response.status_code == 404:
            return jsonify({'message': 'Invalid credentials'}), 401
        else:
            return jsonify({'message': 'Error communicating with IOService'}), 500
        
    return render_template('login.html')

metrics = PrometheusMetrics(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
