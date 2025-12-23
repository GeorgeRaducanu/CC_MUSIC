from flask import Flask, request, jsonify, render_template, redirect, url_for, current_app
import requests
from prometheus_flask_exporter import PrometheusMetrics
import logging
import jwt
import os
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cheia_mea_ultra_secreta_si_smechera'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

metrics = PrometheusMetrics(app)
logging.basicConfig(level=logging.INFO)

AUTH_SERVICE_URL = 'http://auth-service:5000'
IO_SERVICE_URL = 'http://io-service:5001'

SECRET_KEY = os.getenv('SECRET_KEY', 'cheia_mea_ultra_secreta_si_smechera') # Use the same default or get from env

# globale pentru date stocate intern
current_user_id = -1

def generate_token(user_id, role):
    token = jwt.encode({
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def validate_token(required_roles=[]):
    """
    Validates the JWT token found in the Authorization header (Bearer scheme)
    or as a query parameter named 'token'.
    Returns (bool, str): (is_valid, message)
    """
    token = None
    auth_header = request.headers.get('Authorization')
    query_token = request.args.get('token')

    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    elif query_token:
        token = query_token

    if not token:
        return False, 'Authorization token is missing (expected Bearer header or ?token= query parameter)'

    try:
        # Decode the token locally using the shared secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_role = payload.get('role')

        if not user_role:
            return False, 'Token payload missing role information'

        if user_role not in required_roles:
            logging.warning(f"Permission denied: Role '{user_role}' not in required roles {required_roles}")
            return False, 'Permission denied!'

        # Optionally, you could add more checks here (e.g., check user_id against DB)
        logging.info(f"Token validated successfully for role: {user_role}")
        return True, 'Authorized'

    except jwt.ExpiredSignatureError:
        logging.warning("Token validation failed: Expired signature")
        return False, 'Token has expired!'
    except jwt.InvalidTokenError as e:
        logging.error(f"Token validation failed: Invalid token - {e}")
        return False, 'Token is invalid!'
    except Exception as e:
        # Catch any other unexpected errors during decoding
        logging.error(f"An unexpected error occurred during token validation: {e}")
        return False, 'Token validation failed due to an unexpected error'
    
@app.route('/manage_songs', methods=['POST'])
def manage_songs():
    is_valid, message, status_code = validate_token(['admin'])
    if not is_valid:
        return jsonify({"message": message}), status_code
    return jsonify({"message": "Song management endpoint accessed successfully!"})

def decode_token(token):
    logging.info(token)
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        logging.info(decoded_token)
        logging.info(decoded_token.get('user_id'))
        return decoded_token.get('user_id')
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError:
        return "Invalid token"

@app.route('/', methods=['GET'])
def main_page():
    global current_user_id
    folders=[]

    token = request.args.get('token')
    if not token:
        return jsonify({'message': 'Missing token'}), 401

    is_valid, message = validate_token(['admin', 'user'])
    logging.info("Gigel")
    logging.info(is_valid)
    logging.info(message)

    # ar trebui continuat daca is_valid

    current_user_id = decode_token(token)
    logging.info(current_user_id)

    response = requests.post(f"{IO_SERVICE_URL}/get_user_folders", json={'user_id': current_user_id})
    if response.status_code == 200:
        folders = response.json()
        logging.info(folders)
        f = requests.post(f"{IO_SERVICE_URL}/get_folder_songs", json={'folder_id': 1})
        logging.info(f.json())
    elif response.status_code == 404:
        return jsonify({'message': 'Invalid credentials'}), 401
    else:
        return jsonify({'message': 'Error communicating with IOService'}), 500

    return render_template('main.html', folders=folders)

@app.route('/folder/<int:folder_id>', methods=['GET'])
def folder_page(folder_id):
    songs = requests.post(f"{IO_SERVICE_URL}/get_folder_songs", json={'folder_id': folder_id}).json()
    folder_name=requests.post(f"{IO_SERVICE_URL}/get_folder_name", json={'folder_id': folder_id}).json()
    logging.info(songs)
    logging.info(folder_name)
    return render_template("folder_page.html", folder_id=folder_id, songs=songs, folder_name=folder_name)

@app.route('/add_songs/<int:folder_id>', methods=['GET', 'POST'])
def add_songs(folder_id):
    if request.method == 'POST':
        selected_songs = request.form.getlist('songs')
        for song_id in selected_songs:
            requests.post(f"{IO_SERVICE_URL}/add_song_to_folder", json={'folder_id': folder_id, 'song_id': song_id})
        return redirect("/business" + url_for('folder_page', folder_id=folder_id))

    songs = requests.get(f"{IO_SERVICE_URL}/get_all_songs").json()
    current_app.logger.info(songs)
    folder_name = requests.post(f"{IO_SERVICE_URL}/get_folder_name", json={'folder_id': folder_id}).json()
    return render_template('add_songs.html', songs=songs, folder_id=folder_id, folder_name=folder_name)

@app.route('/insert_folder', methods=['POST', 'GET'])
def insert_folder():
    if request.method == 'POST':
        folder_name = request.form['folder_name']
        response = requests.post(f"{IO_SERVICE_URL}/insert_folder", json={'user_id': current_user_id, 'folder_name': folder_name})
        if response.status_code == 200:
            role = requests.post(f"{IO_SERVICE_URL}/get_user_role", json={'user_id': current_user_id}).json().get('role')
            token = generate_token(user_id=current_user_id, role=role)
            return redirect(f"/business/?token={token}")
        else:
            return jsonify({'message': 'Error creating folder'}), 500
    
    return render_template('insert_folder.html')

@app.route('/get_song/<int:song_id>', methods=['GET', 'POST'])
def get_song(song_id):
    response = requests.post(f"{IO_SERVICE_URL}/get_song", json={'song_id': song_id, 'user_id': current_user_id})
    
    app.logger.info(response.json())
    song = response.json()

    return render_template('get_song.html', song=song)

@app.route('/rate_song/<int:song_id>', methods=['POST'])
def rate_song(song_id):
    rating = request.form['rating']
    response = requests.post(f"{IO_SERVICE_URL}/rate_song", json={'song_id': song_id, 'user_id': current_user_id, 'rating': rating})
    
    if response.status_code == 200:
        return redirect("/business/" + url_for('get_song', song_id=song_id))
    else:
        return jsonify({'message': 'Error rating song'}), 500

@app.route('/insert_song_in_db', methods=['POST', 'GET'])
def insert_song_in_db():
    if request.method == 'POST':
        song_title = request.form['song_title']
        song_url = request.form['source_url']
        author_name = request.form['author_name']
        response = requests.post(f"{IO_SERVICE_URL}/insert_song_and_author", json={'song_title': song_title, 'song_url': song_url, 'author_name': author_name})
        if response.status_code == 200:
            role = requests.post(f"{IO_SERVICE_URL}/get_user_role", json={'user_id': current_user_id}).json().get('role')
            token = generate_token(user_id=current_user_id, role=role)
            return redirect(f"/business/?token={token}")
        else:
            return jsonify({'message': 'Error creating folder'}), 500
    
    return render_template('insert_song_in_db.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)