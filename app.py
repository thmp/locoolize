import datetime
import os
import random

from flask import Flask, request, abort, Response, redirect, url_for, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "mov"}
UPLOAD_FOLDER = './uploads'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)


# -- Database definition

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    valid_until = db.Column(db.DateTime, nullable=False)

    photo_url = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    message = db.Column(db.TEXT, nullable=True)

    def __repr__(self):
        return '<Post %r>' % self.id

    def to_json(self):
        return {
            "author": self.author,
            #"created_at": self.created_at,
            #"valid_until": self.valid_until,
            "photo_url": self.photo_url,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "message": self.message,
        }


# -- API Endpoints

@app.route('/')
def index():
    return Response('Locoolize API')

@app.route('/posts', methods=['GET', 'POST'])
def get_posts():
    if request.method == 'POST':
        post_json = request.get_json()

    else:
        LAT_DIFF = 0.1
        LONG_DIFF = 0.1

        latitude = float(request.args.get('lat'))
        longitude = float(request.args.get('long'))

        if latitude is None or longitude is None:
            return abort(400)

        min_lat = latitude - LAT_DIFF
        max_lat = latitude + LAT_DIFF

        min_long = longitude - LONG_DIFF
        max_long = longitude + LONG_DIFF

        posts = Post.query.filter(Post.latitude.between(min_lat, max_lat))\
            .filter(Post.longitude.between(min_long, max_long))\
            .filter(Post.valid_until > datetime.datetime.utcnow())

        return jsonify([post.to_json() for post in posts])

@app.route('/posts/<id>')
def get_post(id):
    post = Post.query.filter_by(id=id).first()
    return jsonify(post.to_json())

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part

        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = "%032x.jpg" % random.getrandbits(128)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # create entry
            # valid_until = request.form.get('valid_until') # todo create datetime from it
            valid_until = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')
            message = request.form.get('message')

            post = Post(created_at=datetime.datetime.utcnow(),
                        valid_until=valid_until,
                        photo_url="/uploads/" + filename,
                        latitude=latitude,
                        longitude=longitude,
                        message=message)

            db.session.add(post)
            db.session.commit()

            return redirect(url_for('uploaded_file', filename=filename))

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''