from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB limit

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    conn = sqlite3.connect('streamhub.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  filename TEXT NOT NULL,
                  views INTEGER DEFAULT 0,
                  upload_date TEXT NOT NULL)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('streamhub.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos ORDER BY upload_date DESC")
    videos = c.fetchall()
    conn.close()
    return render_template('index.html', videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        file = request.files['video']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            conn = sqlite3.connect('streamhub.db')
            c = conn.cursor()
            c.execute("INSERT INTO videos (title, filename, upload_date) VALUES (?,?,?)",
                      (title, filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/watch/<int:video_id>')
def watch(video_id):
    conn = sqlite3.connect('streamhub.db')
    c = conn.cursor()
    c.execute("UPDATE videos SET views = views + 1 WHERE id =?", (video_id,))
    c.execute("SELECT * FROM videos WHERE id =?", (video_id,))
    video = c.fetchone()
    conn.close()
    if video:
        return render_template('watch.html', video=video)
    return "Video not found", 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5002)