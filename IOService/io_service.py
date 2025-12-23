import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, request, jsonify
from flask import Flask, render_template, redirect, url_for, session, flash, current_app
from prometheus_flask_exporter import PrometheusMetrics
import logging

logging.basicConfig(level=logging.INFO)
io_bp = Blueprint('io_service', __name__)

DATABASE_CONFIG = {
    'dbname': 'idp_music',
    'user': 'admin',  # Use the correct user
    'password': 'admin',  # Use the correct password
    'host': 'postgres-db',
    'port': 5432
}

def getDB():
    conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
    return conn

def get_user_role_by_id(user_id):
    conn = getDB()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id=%s", (user_id,))
    role = cursor.fetchone()
    conn.close()
    return role

def get_user_by_name_and_password(username, password):
    conn = getDB()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def get_folder_name_by_id(folder_id):
    conn = getDB()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM folders WHERE id=%s", (folder_id,))
    name = cursor.fetchone()
    conn.close()
    return name

def get_folders(user_id):
    conn = getDB()
    cursor = conn.cursor()
    cursor.execute("SELECT f.id, f.name FROM folders f JOIN user_folders uf ON f.id = uf.folder_id WHERE uf.user_id=%s", (user_id,))
    folders = cursor.fetchall()
    conn.close()
    return [dict(row) for row in folders]

def get_songs_from_folder(folder_id):
    conn = getDB()
    cursor = conn.cursor()
    cursor.execute("SELECT s.id, s.title, s.source_url, STRING_AGG(a.name, ', ') AS authors FROM songs s JOIN folder_songs fs ON s.id = fs.song_id JOIN song_authors sa ON s.id = sa.song_id JOIN authors a ON sa.author_id = a.id WHERE fs.folder_id=%s GROUP BY s.id, s.title", (folder_id,))
    songs = cursor.fetchall()
    conn.close()
    return [dict(row) for row in songs]

def get_song_by_id(song_id, user_id):
    conn = getDB()
    cursor = conn.cursor()
    #cursor.execute("SELECT s.id, s.title, s.source_url, STRING_AGG(a.name, ', ') AS authors, us.rating FROM songs s JOIN song_authors sa ON s.id = sa.song_id JOIN authors a ON sa.author_id = a.id LEFT JOIN song_ratings us ON s.id = us.song_id AND us.user_id = %s WHERE s.id=%s GROUP BY s.id, us.rating", (user_id, song_id))
    cursor.execute(
            """
            SELECT
                s.id,
                s.title,
                s.source_url,
                STRING_AGG(DISTINCT a.name, ', ') AS authors,
                usr.rating, -- Specific user's rating
                AVG(all_ratings.rating) AS average_rating -- Average rating from all users
            FROM
                songs s
            LEFT JOIN -- Use LEFT JOIN in case a song has no authors (unlikely but safe)
                song_authors sa ON s.id = sa.song_id
            LEFT JOIN
                authors a ON sa.author_id = a.id
            LEFT JOIN
                song_ratings usr ON s.id = usr.song_id AND usr.user_id = %s -- Join for specific user's rating
            LEFT JOIN
                song_ratings all_ratings ON s.id = all_ratings.song_id -- Join for calculating average
            WHERE
                s.id = %s
            GROUP BY
                s.id, s.title, s.source_url, usr.rating -- Group by all non-aggregated columns
            """,
            (user_id, song_id)
        )
    song = cursor.fetchone()
    conn.close()
    return song

def rate_song_id(song_id, user_id, rating):
    conn = getDB()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO song_ratings (song_id, user_id, rating) VALUES (%s, %s, %s) ON CONFLICT (song_id, user_id) DO UPDATE SET rating = EXCLUDED.rating", (song_id, user_id, rating))
    conn.commit()
    conn.close()

def add_folder(user_id, folder_name):
    conn = getDB()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO folders (name) VALUES (%s) RETURNING id", (folder_name,))
    folder_id_row = cursor.fetchone()
    folder_id = folder_id_row['id']
    cursor.execute("INSERT INTO user_folders (user_id, folder_id) VALUES (%s, %s)", (user_id, folder_id))
    conn.commit()
    conn.close()
    current_app.logger.info(f"Folder {folder_name} added with ID {folder_id}")
    if not folder_id:
        raise Exception("Folder insertion failed to return ID")
    return folder_id

def add_song(song_name, song_url):
    conn = getDB()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO songs (title, source_url) VALUES (%s, %s) RETURNING id", (song_name, song_url))
    song_id = cursor.fetchone()['id']
    conn.commit()
    conn.close()
    return song_id

def add_author(author_name):
    conn = getDB()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM authors WHERE name = %s", (author_name,))
    existing_author = cursor.fetchone()
    if existing_author:
        author_id = existing_author['id']
        current_app.logger.info(f"Author '{author_name}' already exists with ID: {author_id}")
    else:
        cursor.execute("INSERT INTO authors (name) VALUES (%s) RETURNING id", (author_name,))
        author_id = cursor.fetchone()['id']
    conn.commit()
    conn.close()
    return author_id

def add_song_regards_author(song_name, song_url, author_name, author_id):
    conn = getDB()
    cursor = conn.cursor()

    # 1. Check if this author is already linked to a song with this title
    cursor.execute(
        """
        SELECT sa.song_id
        FROM song_authors sa
        JOIN songs s ON sa.song_id = s.id
        WHERE sa.author_id = %s AND s.title = %s
        """,
        (author_id, song_name)
    )
    existing_link = cursor.fetchone()
    if existing_link:
        song_id = existing_link['song_id']
    else:
        song_id = add_song(song_name, song_url)
        if song_id:
            cursor.execute("INSERT INTO song_authors (song_id, author_id) VALUES (%s, %s)", (song_id, author_id))
            conn.commit()

@io_bp.route('/get_user', methods=['POST'])
def get_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Missing credentials'}), 400
    
    user = get_user_by_name_and_password(username, password)
    if user:
        return jsonify(dict(user)), 200
    else:
        return jsonify({'message': 'User not found'}), 404

@io_bp.route('/get_user_folders', methods=['POST'])
def get_user_folders():
    data = request.json
    user_id = data.get('user_id')

    folders = get_folders(user_id)
    logging.info(folders)

    if folders:
        return jsonify(folders), 200
    else:
        return jsonify({'message': 'User not found with the given ID'}), 404

@io_bp.route('/get_folder_songs', methods=['POST'])
def get_folder_songs():
    data = request.json
    folder_id = data.get('folder_id')

    songs = get_songs_from_folder(folder_id)
    logging.info(songs)

    return jsonify(songs), 200

@io_bp.route('/get_folder_name', methods=['POST'])
def get_folder_name():
    data = request.json
    folder_id = data.get('folder_id')

    name = get_folder_name_by_id(folder_id)
    logging.info(name)

    return jsonify(name), 200

@io_bp.route('/insert_user', methods=['POST'])
def insert_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')  # Default role is 'user'

    if not username or not password:
        return jsonify({'message': 'Missing credentials'}), 400

    try:
        conn = getDB()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s) RETURNING id",
            (username, password, f"{username}@example.com", role)
        )
        user_result = cursor.fetchone()
        if not user_result:
             raise Exception("User insertion failed to return ID")
        user_id = user_result['id']

        cursor.execute("INSERT INTO folders (name) VALUES ('Favourites') RETURNING id")
        fav_result = cursor.fetchone()
        if not fav_result:
             raise Exception("Favourites folder insertion failed to return ID")
        favourites_id = fav_result['id']

        cursor.execute("INSERT INTO folders (name) VALUES ('Listen Later') RETURNING id")
        listen_later_result = cursor.fetchone()
        if not listen_later_result:
             raise Exception("Listen Later folder insertion failed to return ID")
        listen_later_id = listen_later_result['id']

        cursor.execute("INSERT INTO user_folders (user_id, folder_id) VALUES (%s, %s)", (user_id, favourites_id))
        cursor.execute("INSERT INTO user_folders (user_id, folder_id) VALUES (%s, %s)", (user_id, listen_later_id))
        conn.commit()
        conn.close()
        return jsonify({'id': user_id, 'username': username, 'role': role}), 200
    except psycopg2.IntegrityError:
        return jsonify({'message': 'User already exists'}), 409
    except Exception as e:
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500

@io_bp.route('/get_all_songs', methods=['GET'])
def get_all_songs():
    conn = getDB()
    cursor = conn.cursor()
    cursor.execute("SELECT s.id, s.title, STRING_AGG(a.name, ', ') AS authors FROM songs s JOIN song_authors sa ON s.id = sa.song_id JOIN authors a ON sa.author_id = a.id GROUP BY s.id, s.title")
    songs = cursor.fetchall()
    conn.close()
    return jsonify([dict(song) for song in songs]), 200

@io_bp.route('/add_song_to_folder', methods=['POST'])
def add_song_to_folder():
    data = request.json
    folder_id = data.get('folder_id')
    song_id = data.get('song_id')

    conn = getDB()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO folder_songs (folder_id, song_id) VALUES (%s, %s)", (folder_id, song_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Song added to folder'}), 200

@io_bp.route('/insert_folder', methods=['POST'])
def insert_folder():
    data = request.json
    user_id = data.get('user_id')
    folder_name = data.get('folder_name')

    folder_id = add_folder(user_id, folder_name)
    return jsonify({'folder_id': folder_id}), 200

@io_bp.route('/get_user_role', methods=['POST'])
def get_user_role():
    data = request.json
    user_id = data.get('user_id')

    role = get_user_role_by_id(user_id)
    if role:
        return jsonify(role), 200
    else:
        return jsonify({'message': 'User not found'}), 404

@io_bp.route('/get_song', methods=['POST'])
def get_song():
    data = request.json
    song_id = data.get('song_id')
    user_id = data.get('user_id')
    song = get_song_by_id(song_id, user_id)

    app.logger.info(song)

    if song:
        return jsonify(dict(song)), 200
    else:
        return jsonify({'message': 'Song not found'}), 404

@io_bp.route('/rate_song', methods=['POST'])
def rate_song():
    data = request.json
    song_id = data.get('song_id')
    user_id = data.get('user_id')
    rating = data.get('rating')

    if not song_id or not user_id or not rating:
        return jsonify({'message': 'Missing parameters'}), 400

    try:
        rate_song_id(song_id, user_id, rating)
        return jsonify({'message': 'Rating updated successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500
    
@io_bp.route('/insert_song', methods=['POST'])
def insert_song():
    data = request.json
    song_name = data.get('song_title')
    song_url = data.get('song_url')

    song_id = add_song(song_name, song_url)
    return jsonify({'song_id': song_id}), 200

@io_bp.route('/insert_author', methods=['POST'])
def insert_author():
    data = request.json
    author_name = data.get('author_name')

    author_id = add_author(author_name)
    
    return jsonify({'author_id': author_id}), 200

@io_bp.route('/insert_song_and_author', methods=['POST'])
def insert_song_and_author():
    data = request.json
    song_name = data.get('song_title')
    song_url = data.get('song_url')
    author_name = data.get('author_name')

    author_id = add_author(author_name)
    # Verific daca exista melodie asta la autorul respectiv in baza de date
    song_id = add_song_regards_author(song_name, song_url, author_name, author_id)

    return jsonify({'song_id': song_id, 'author_id': author_id}), 200

app = Flask(__name__)
app.register_blueprint(io_bp)
metrics = PrometheusMetrics(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
